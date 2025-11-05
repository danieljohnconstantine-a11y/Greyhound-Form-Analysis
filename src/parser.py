# src/parser.py
# Full replacement: header parser (kept compatible) + “no-miss” Section 2 extractor.
# - Robust header parsing (compatible with your existing format; supports short track codes)
# - Guarantees RaceNumber/Track/Distance columns
# - Auto race numbering fallback
# - Deep Section 2 enrichment:
#     * normalization
#     * multi-anchor + fuzzy block finding
#     * exact regex rules
#     * token scanning (word-by-word)
#     * recent runs extractor (list-of-dicts)
# - Safe to run even if some fields are missing

import re
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ---------- Optional: fuzzy matcher (rapidfuzz). If unavailable, fall back gracefully ----------
try:
    from rapidfuzz import fuzz
    _FUZZY_OK = True
except Exception:
    _FUZZY_OK = False
    logger.warning("rapidfuzz not available - fuzzy matching disabled")


# =========================================
# ============ HEADER PARSER ==============
# =========================================

_TRACK_MAP = {
    "RICHG": "Richmond", "RICH": "Richmond",
    "WENTW": "Wentworth Park", "WENT": "Wentworth Park",
    "ALBPK": "Albion Park", "ALB": "Albion Park",
    "DARW": "Darwin", "DARWIN": "Darwin",
    "DAPTO": "Dapto", "GOSF": "Gosford",
    "SAND": "Sandown Park", "SANDOWN": "Sandown Park",
    "GRAFT": "Grafton", "BATH": "Bathurst",
    "MAND": "Mandurah", "CANN": "Cannington",
    "LADB": "Ladbrokes Gardens", "HORS": "Horsham",
    "WARR": "Warrnambool", "TRAR": "Traralgon",
    "BALL": "Ballarat", "GEEL": "Geelong",
}

def _normalize_track(track_raw: str) -> str:
    t = (track_raw or "").strip()
    if not t:
        return "UNKNOWN"
    key = t.upper().split()[0][:5]
    return _TRACK_MAP.get(key, t.title())


def parse_race_form(text: str) -> pd.DataFrame:
    """
    Parse greyhound race form text into a structured DataFrame.
    
    This function performs two-phase parsing:
    
    Phase 1: Extract race headers and basic dog info from tabular section
    - Parses race number, time, track, distance from header lines
    - Extracts box, name, trainer, career stats from dog rows
    - Handles missing race numbers with auto-numbering fallback
    
    Phase 2: Enrich with detailed dog information from Section 2
    - Extracts breeding (sire/dam), owner, performance metrics
    - Captures recent race history for each dog
    - All extraction errors are handled gracefully
    
    Args:
        text: Raw text extracted from greyhound racing form PDF/document
        
    Returns:
        DataFrame with one row per dog, containing all available fields.
        Missing fields are set to None rather than causing errors.
    """
    lines = text.splitlines()
    dogs = []
    current_race = {}
    race_number = 0

    # Header pattern compatible with your existing repo; supports short codes and extra spaces.
    header_re = re.compile(
        r"Race No\s*(\d{1,2}).*?(\d{2}:\d{2}[AP]M)\s+([A-Za-z0-9 ]+?)\s+(\d{3})m",
        re.I,
    )

    # Dog row pattern (kept as in your repo for header table):
    dog_re = re.compile(
        r"""^(\d+)\.?\s*([0-9]{3,6})?([A-Za-z'’\- ]+)\s+(\d+[a-z])\s+([\d.]+)kg\s+(\d+)\s+([A-Za-z'’\- ]+)\s+(\d+)\s*-\s*(\d+)\s*-\s*(\d+)\s+\$([\d,]+)\s+(\S+)\s+(\S+)\s+(\S+)""",
        re.I,
    )

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        m_head = header_re.match(line)
        if m_head:
            race_number += 1
            _, time_str, track_raw, dist = m_head.groups()
            current_race = {
                "RaceNumber": race_number,
                "RaceDate": "",  # keep as-is (your pipeline may set this elsewhere)
                "RaceTime": time_str,
                "Track": _normalize_track(track_raw),
                "Distance": int(dist),
            }
            continue

        m_dog = dog_re.match(line)
        if m_dog:
            (
                box, form_number, raw_name, sex_age, weight, draw, trainer,
                wins, places, starts, prize, rtc, dlr, dlw
            ) = m_dog.groups()

            dog_name = (raw_name or "").strip()
            # handle glued form numbers at start of name (your original logic)
            if form_number and dog_name.startswith(form_number[-2:] or ""):
                dog_name = dog_name[len(form_number[-2:]):].strip()

            dogs.append({
                "Box": int(box),
                "DogName": dog_name.upper(),
                "FormNumber": form_number or "",
                "Trainer": (trainer or "").strip(),
                "SexAge": sex_age,
                "Weight": float(weight),
                "Draw": int(draw),
                "CareerWins": int(wins),
                "CareerPlaces": int(places),
                "CareerStarts": int(starts),
                "PrizeMoney": float(prize.replace(",", "")),
                "RTC": rtc,
                "DLR": dlr,
                "DLW": dlw,
                **current_race
            })
            continue

    df = pd.DataFrame(dogs)

    # Safety: ensure critical columns exist
    for col in ["RaceNumber", "Track", "Distance"]:
        if col not in df.columns:
            df[col] = None

    # Auto race numbering if header was missed
    if len(df) and df["RaceNumber"].isna().any():
        current = 1
        for i in df.index:
            if df.at[i, "Box"] == 1 and i != 0:
                current += 1
            df.at[i, "RaceNumber"] = current

    # Phase 2: Section 2 enrichment
    df = _enrich_section2(df, text, debug=False)

    enriched = df.get('Owner').notna().sum() if 'Owner' in df.columns else 0
    logger.info(f"✅ Parsed {len(df)} dogs total ({enriched} with enriched details)")
    return df


# =========================================
# ========== SECTION 2 ENRICHER ===========
# =========================================

# Known distances for fallback/repair
_KNOWN_DISTANCES = {
    288,300,301,305,312,319,320,331,350,380,383,400,401,407,425,431,440,
    450,457,460,472,480,484,500,515,520,525,530,545,565,600,603,642,650,
    685,700,710,715,720,731,750,760,800,842
}

# Normalization
def _norm(txt: str) -> str:
    t = txt.replace("\r", "\n")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n[ \t]+", "\n", t)
    t = t.replace("–", "-").replace("—", "-").replace("’", "'").replace("‘", "'")
    t = t.replace(" Kg", " kg").replace("KG", "kg")
    # Collapse multiple consecutive newlines to max 2 (preserve line breaks!)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t

# Multi-anchor + fuzzy block finding
def _compile_block_patterns(name: str):
    """
    Create regex patterns to extract a single dog's detail block.
    The pattern must stop at the next dog's name (uppercase line followed by j50s/j350s).
    """
    esc = re.escape(name)
    # Match from dog name to either:
    # - Next dog name pattern: uppercase word(s) on own line followed by j50s/j350s pattern
    # - End of text
    # Use negative lookahead to not consume the next dog's name
    next_dog_pattern = r"(?=\n[A-Z][A-Z0-9' \-]+\s*\n\s*j\d+s\s+j\d+s|\Z)"
    
    return [
        # Pattern 1: Dog name followed by content until next dog or end
        re.compile(rf"^{esc}\s*$.*?{next_dog_pattern}", re.M | re.S),
        # Pattern 2: More flexible - just find the name and grab content
        re.compile(rf"{esc}.*?{next_dog_pattern}", re.S),
    ]

def _find_block(full_text: str, name: str, all_names_upper):
    """
    Find and extract a single dog's detail block from the full text.
    Returns only the content for this specific dog, stopping at the next dog's section.
    """
    # Try exact patterns first
    for pat in _compile_block_patterns(name):
        m = pat.search(full_text)
        if m:
            return m.group(0)

    # Fuzzy matching (if available)
    if _FUZZY_OK:
        candidates = re.findall(r"[A-Z][A-Z0-9' \-]{2,}", full_text)
        best = None
        best_score = 0
        for c in set(candidates):
            sc = fuzz.partial_ratio(name, c)
            if sc > best_score:
                best_score = sc
                best = c
        if best and best_score > 80:
            for pat in _compile_block_patterns(best):
                m = pat.search(full_text)
                if m:
                    return m.group(0)

    # Sliding window fallback with better boundary detection
    i = full_text.find(name)
    if i != -1:
        # Find start of this dog's section (should be at a line start)
        start = full_text.rfind('\n', max(0, i-10), i)
        if start == -1:
            start = 0
        else:
            start += 1  # Move past the newline
        
        # Look for next dog section: uppercase name followed by j50s pattern
        window = full_text[start:]
        # Find the end: next occurrence of pattern "DOGNAME\nj50s j350s" after current position
        next_dog = re.search(r'\n([A-Z][A-Z0-9\' \-]+)\s*\nj\d+s\s+j\d+s', window[len(name)+10:])
        if next_dog:
            end = start + len(name) + 10 + next_dog.start()
            return full_text[start:end]
        else:
            # No next dog found, take rest of text (up to reasonable limit)
            return window[:4000]
    
    return None

# Regex rules
_FIELD_RX = {
    "colour_sex_age": re.compile(r"0\s*kg\s*\(?\d+\)?\s*([a-z/]+)\s+(\d+)\s+([DB])", re.I),
    "sire_dam": re.compile(r"([A-Z][A-Za-z0-9' ()]+)\s*-\s*([A-Z][A-Za-z0-9' ()]+?)(?:\s+J/T:|\s*\n|$)"),
    "raced_distance": re.compile(r"Raced\s*Distance:\s*([\d\-]+)", re.I),
    "winning_distance": re.compile(r"Winning\s*Distance:\s*([A-Za-z0-9]+)", re.I),
    "owner": re.compile(r"Owner:\s*(.+?)(?=\s*(?:\n|CarPM/s|Dog:|Trainer:|$))", re.I),
    "dog_record": re.compile(r"(?:Dog|Horse):\s*(\d+-\d+-\d+)\s+(\d+%)\s*-\s*(\d+%)", re.I),
    "trainer_stats": re.compile(r"J/T:\s.*?(\d+-\d+-\d+)\s+(\d+%-\d+%)", re.I),
    "api": re.compile(r"\bAPI\b\s+([\d.]+)", re.I),
    "carpm": re.compile(r"\bCarPM/s\b\s+([\d.,]+)", re.I),
    "pm12": re.compile(r"\b12mPM/s\b\s+([\d.,/]+)", re.I),
    "rtc_km": re.compile(r"\bRTC\/km\b\s+([\d./]+)", re.I),
    "rdisttc": re.compile(r"\bRDistTC\b\s+(\d+)", re.I),
    "dls": re.compile(r"\bDLS(?:the)?\b\s+(\d+)", re.I),
    "dlw": re.compile(r"\bDLW\b\s+(\d+)", re.I),
    "dod": re.compile(r"\bDOD\b\s+(\d+)", re.I),
    "grade_G1": re.compile(r"\bG1\b\s+(\d+-\d+-\d+)", re.I),
    "grade_G2": re.compile(r"\bG2\b\s+(\d+-\d+-\d+)", re.I),
    "grade_G3": re.compile(r"\bG3\b\s+(\d+-\d+-\d+)", re.I),
    "grade_LR": re.compile(r"\bLR\b\s+(\d+-\d+-\d+)", re.I),
    "grade_FU": re.compile(r"\bFU\b\s+(\d+-\d+-\d+)", re.I),
    "grade_2U": re.compile(r"\b2U\b\s+(\d+-\d+-\d+)", re.I),
    "grade_3U": re.compile(r"\b3U\b\s+(\d+-\d+-\d+)", re.I),
}

# Token scanning for times/margins/prize/distances/track in block text
def _scan_tokens(block: str):
    out = {
        "DetectedDistance": None,
        "LastPrize": None,
        "LastMargin": None,
        "LastRaceTime": None,
        "LastSecTime": None,
        "LastTrack": None,
    }
    words = block.split()
    for i, w in enumerate(words):
        # Distances like 401m
        if re.fullmatch(r"\d{3}m", w):
            d = int(w[:-1])
            if d in _KNOWN_DISTANCES:
                out["DetectedDistance"] = d
        # Prize
        if w.lower() == "prize" and i+1 < len(words):
            nxt = words[i+1]
            if re.match(r"^\$?\d[\d,]*(?:\.\d+)?$", nxt):
                out["LastPrize"] = nxt.lstrip("$").replace(",", "")
        # Margin
        if w.lower() == "margin" and i+1 < len(words):
            nxt = words[i+1]
            if re.match(r"^[\d.]+$", nxt):
                out["LastMargin"] = nxt
        # Race Time
        if w.lower() == "time" and i > 0 and words[i-1].lower() == "race":
            if i+1 < len(words) and re.match(r"^\d+:\d{2}\.\d{2}$", words[i+1]):
                out["LastRaceTime"] = words[i+1]
        # Sec Time
        if w.lower() == "time" and i > 0 and words[i-1].lower() == "sec":
            if i+1 < len(words) and re.match(r"^\d{1,2}\.\d{2}$", words[i+1]):
                out["LastSecTime"] = words[i+1]
        # Track name presence in results lines
        if w.upper() in {"DARWIN","RICHMOND","WENTWORTH","ALBION","MANDURAH",
                         "GOSFORD","SANDOWN","CANNINGTON","DUBBO","BATHURST","GRAFTON"}:
            out["LastTrack"] = w.title()
    return out

# Recent runs extractor (list of dicts)
_RUN_LINE = re.compile(
    r"""
    (?P<pos>\d+(?:st|nd|rd|th))\s+of\s+(?P<field>\d+)\s+
    (?P<date>\d{1,2}/\d{2}/\d{4})\s+
    (?P<track>[A-Z][A-Za-z]+)\s+
    (?:Margin\s+(?P<margin>[\d.]+)\s+Lengths\s+)?
    (?:Distance\s+(?P<distance>\d{3})m\s+)?
    (?:SOT\s+(?P<sot>[A-Z])\s+)?
    (?:RST\s+(?P<rst>[A-Z/]+)\s+)?
    (?:GR\s+(?P<grade>[\w/]+)\s+)?
    (?:Race\s+(?P<race_name>.+?)\s+)?
    (?:Prize\s+\$(?P<prize>[\d,]+)\s+)?
    (?:API\s+(?P<api>[\d.]+)\s+)?
    (?:Race\s+Time\s+(?P<racetime>\d+:\d{2}\.\d{2})\s+)?
    (?:Sec\s+Time\s+(?P<sectime>\d{1,2}\.\d{2})\s+)?
    (?:BP\s+(?P<bp>\d+)\s+)?
    (?:Odds\s+(?P<odds>[\d.]+F?)\s+)?
    (?:Trainer\s+(?P<trainer>[A-Za-z' -]+?)\s+)?
    (?:Ongoing\s+Winners\s+(?P<og>[0-9\-]+)\s+)?
    (?:Track\s+Direction\s+(?P<dir>[A-Za-z\-]+)\s+)?
    (?:Winner\s+(?P<winner>[A-Za-z' ]+?)\s+\((?P<wbox>\d)\)\s+)?
    (?:Second\s+(?P<second>[A-Za-z' ]+?)\s+\((?P<sbox>\d)\)\s+)?
    (?:Third\s+(?P<third>[A-Za-z' ]+?)\s+\((?P<tbox>\d)\)\s+)?
    """,
    re.I | re.X,
)

def _extract_recent_runs(block: str):
    """
    Extract recent race results from a dog's detail block.
    Tolerates malformed lines and continues parsing even if some results are invalid.
    """
    runs = []
    try:
        candidates = re.split(r"(?=(?:\d{1,2}(?:st|nd|rd|th)\s+of\s+\d+))", block)
        for cand in candidates:
            cand = cand.strip()
            if not cand:
                continue
            try:
                m = _RUN_LINE.search(cand)
                if not m:
                    continue
                d = m.groupdict()
                # Clean up prize field if present
                if d.get("prize"):
                    d["prize"] = d["prize"].replace(",", "")
                runs.append(d)
            except Exception as e:
                # Log but don't crash on malformed race result line
                logger.debug(f"Failed to parse race result line: {e}")
                continue
    except Exception as e:
        logger.warning(f"Error extracting recent runs: {e}")
    
    return runs

def _extract_fields(block: str):
    """
    Extract all dog detail fields from a block of text.
    Handles missing or malformed fields gracefully - returns None for missing values.
    All extraction failures are logged but do not stop processing.
    """
    out = {
        "Colour": None, "Sex": None, "Age": None,
        "Sire": None, "Dam": None,
        "RacedDistance": None, "WinningDistance": None,
        "Owner": None,
        "DogRecord": None, "WinPercent": None, "PlacePercent": None,
        "Trainer50": None, "Trainer350": None,
        "CarPM/s": None, "12mPM/s": None, "API": None,
        "RTC/km": None, "RDistTC": None, "DLS": None, "DLW": None, "DOD": None,
        "G1": None, "G2": None, "G3": None, "LR": None, "FU": None, "2U": None, "3U": None,
        "DetectedDistance": None, "LastPrize": None, "LastMargin": None,
        "LastRaceTime": None, "LastSecTime": None, "LastTrack": None,
        "RecentRuns": None,
    }

    # Extract colour, sex, age with error handling
    try:
        m = _FIELD_RX["colour_sex_age"].search(block)
        if m:
            out["Colour"] = m.group(1).lower()
            out["Age"] = m.group(2)
            out["Sex"] = "Dog" if m.group(3).upper() == "D" else "Bitch"
    except Exception as e:
        logger.debug(f"Failed to extract colour/sex/age: {e}")

    # Extract sire and dam
    try:
        m = _FIELD_RX["sire_dam"].search(block)
        if m:
            out["Sire"] = m.group(1).strip()
            out["Dam"] = m.group(2).strip()
    except Exception as e:
        logger.debug(f"Failed to extract sire/dam: {e}")

    # Extract distance fields
    try:
        m = _FIELD_RX["raced_distance"].search(block)
        out["RacedDistance"] = m.group(1) if m else None
    except Exception as e:
        logger.debug(f"Failed to extract raced distance: {e}")
    
    try:
        m = _FIELD_RX["winning_distance"].search(block)
        out["WinningDistance"] = m.group(1) if m else None
    except Exception as e:
        logger.debug(f"Failed to extract winning distance: {e}")

    # Extract owner
    try:
        m = _FIELD_RX["owner"].search(block)
        if m:
            out["Owner"] = re.sub(r"\s+", " ", m.group(1)).strip()
    except Exception as e:
        logger.debug(f"Failed to extract owner: {e}")

    # Extract dog record stats
    try:
        m = _FIELD_RX["dog_record"].search(block)
        if m:
            out["DogRecord"], out["WinPercent"], out["PlacePercent"] = m.group(1), m.group(2), m.group(3)
    except Exception as e:
        logger.debug(f"Failed to extract dog record: {e}")

    # Extract trainer stats
    try:
        m = _FIELD_RX["trainer_stats"].search(block)
        if m:
            out["Trainer50"], out["Trainer350"] = m.group(1), m.group(2)
    except Exception as e:
        logger.debug(f"Failed to extract trainer stats: {e}")

    # Extract numeric fields with individual error handling
    field_mappings = [
        ("api", "API"),
        ("carpm", "CarPM/s"),
        ("pm12", "12mPM/s"),
        ("rtc_km", "RTC/km"),
        ("rdisttc", "RDistTC"),
        ("dls", "DLS"),
        ("dlw", "DLW"),
        ("dod", "DOD"),
    ]
    
    for key, col in field_mappings:
        try:
            m = _FIELD_RX[key].search(block)
            if m:
                val = m.group(1)
                # Remove commas from numeric values
                if key in ["carpm"] and val:
                    val = val.replace(",", "")
                out[col] = val
        except Exception as e:
            logger.debug(f"Failed to extract {col}: {e}")

    # Extract grade fields
    for key, col in [("grade_G1","G1"),("grade_G2","G2"),("grade_G3","G3"),
                     ("grade_LR","LR"),("grade_FU","FU"),("grade_2U","2U"),("grade_3U","3U")]:
        try:
            m = _FIELD_RX[key].search(block)
            if m:
                out[col] = m.group(1)
        except Exception as e:
            logger.debug(f"Failed to extract grade {col}: {e}")

    # Token scan fallbacks
    try:
        tk = _scan_tokens(block)
        for k, v in tk.items():
            if v:
                out[k] = v
    except Exception as e:
        logger.debug(f"Failed token scanning: {e}")

    # Recent runs list
    try:
        runs = _extract_recent_runs(block)
        if runs:
            out["RecentRuns"] = runs
    except Exception as e:
        logger.warning(f"Failed to extract recent runs: {e}")

    return out


def _enrich_section2(df: pd.DataFrame, full_text: str, debug: bool = False) -> pd.DataFrame:
    """
    Enrich header-parsed df with Section 2 details. Adds many new columns and
    populates df['RecentRuns'] (list-of-dicts). Repairs Distance if missing.
    
    Handles all extraction errors gracefully - continues processing even if individual
    dogs fail to parse. All errors are logged for debugging.
    """
    try:
        txt = _norm(full_text)
    except Exception as e:
        logger.error(f"Failed to normalize text: {e}")
        return df

    ensure_cols = [
        "Colour", "Sex", "Age", "Sire", "Dam",
        "RacedDistance", "WinningDistance", "Owner",
        "DogRecord", "WinPercent", "PlacePercent",
        "Trainer50", "Trainer350", "CarPM/s", "12mPM/s", "API",
        "RTC/km", "RDistTC", "DLS", "DLW", "DOD",
        "G1", "G2", "G3", "LR", "FU", "2U", "3U",
        "DetectedDistance", "LastPrize", "LastMargin",
        "LastRaceTime", "LastSecTime", "LastTrack",
        "RecentRuns",
    ]
    for c in ensure_cols:
        if c not in df.columns:
            df[c] = None

    names_upper = [str(n).upper().strip() for n in df["DogName"].fillna("")]
    matched = missed = 0
    extraction_errors = 0

    for idx, row in df.iterrows():
        try:
            name = str(row["DogName"]).upper().strip()
            if not name:
                missed += 1
                logger.debug(f"Row {idx}: Empty dog name, skipping")
                continue

            # Find the dog's detail block
            try:
                block = _find_block(txt, name, names_upper)
            except Exception as e:
                logger.warning(f"Error finding block for {name}: {e}")
                missed += 1
                continue
            
            if not block:
                missed += 1
                logger.debug(f"No detail block found for {name}")
                if debug:
                    print(f"[MISS] {name}")
                continue

            # Extract fields from block
            try:
                fields = _extract_fields(block)
            except Exception as e:
                logger.error(f"Error extracting fields for {name}: {e}")
                extraction_errors += 1
                continue

            # Write back fields with error handling
            try:
                for k, v in fields.items():
                    if k == "RecentRuns":
                        if v:
                            df.at[idx, "RecentRuns"] = v
                    else:
                        if v is not None and v != "":
                            df.at[idx, k] = v

                # Distance repair from DetectedDistance
                if ("Distance" in df.columns) and (pd.isna(row.get("Distance")) or not row.get("Distance")):
                    if fields.get("DetectedDistance"):
                        df.at[idx, "Distance"] = fields["DetectedDistance"]
            except Exception as e:
                logger.error(f"Error writing fields for {name}: {e}")
                extraction_errors += 1

            matched += 1
            if debug:
                print(f"[OK] {name}")
                
        except Exception as e:
            logger.error(f"Unexpected error processing row {idx}: {e}")
            extraction_errors += 1
            continue

    if debug:
        print(f"[Section2] Matched={matched} Missed={missed} Errors={extraction_errors}")

    logger.info(f"✅ Enriched {matched} dogs using deep Section 2 parser (missed: {missed}, errors: {extraction_errors})")
    return df


# Optional helper to flatten recent runs if you need a separate table
def explode_recent_runs(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    base_cols = [c for c in df.columns if c != "RecentRuns"]
    for _, dog in df.iterrows():
        runs = dog.get("RecentRuns")
        if not runs:
            continue
        base = {c: dog[c] for c in base_cols}
        for r in runs:
            rows.append({**base, **r})
    return pd.DataFrame(rows)


# ---------- Local test ----------
if __name__ == "__main__":
    # Expect your main to pass in PDF text already; this is an example placeholder.
    path = "data/RICHG1910form.txt"
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except Exception:
        print("⚠️ Local test: sample text not found. Skipping.")
        raise SystemExit(0)

    df = parse_race_form(raw_text)
    pd.set_option("display.max_columns", None)
    print(df.head(12))
