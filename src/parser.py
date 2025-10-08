import re
import pandas as pd
from datetime import datetime

def is_greyhound_race(block):
    return any(name in block for name in [
        "FERNANDO BALE", "ZAMBORA BROCKIE", "KOBLENZ", "KEEPING", "ASTON", "PAW"
    ])

def extract_race_metadata(block, race_number, filename):
    # Extract date from block
    date_match = re.search(r"(\d{2}/\d{2}/\d{4})", block)
    date_str = ""
    if date_match:
        try:
            date_str = datetime.strptime(date_match.group(1), "%d/%m/%Y").strftime("%Y-%m-%d")
        except:
            date_str = ""

    # Infer track from filename
    track_match = re.match(r"([A-Z]{3,})G\d{4}", filename)
    track = track_match.group(1) if track_match else "UNKNOWN"

    # Extract distance
    distance_match = re.search(r"(\d{3,4}m)", block)
    distance = distance_match.group(1) if distance_match else ""

    return {
        "RaceDate": date_str,
        "Track": track,
        "RaceNumber": str(race_number),
        "Distance": distance,
        "Class": "",
        "Weather": "",
        "Surface": ""
    }

def extract_runners(block):
    pattern = r"(\d+)\.\s+([A-Z][A-Za-z\s\-']+).*?Trainer[:\s]+([A-Za-z\s\-']+)"
    matches = re.findall(pattern, block, re.DOTALL)
    runners = []
    for m in matches:
        runners.append({
            "DogName": m[1].strip(),
            "Box": int(m[0]),
            "Trainer": m[2].strip(),
            "PrizeMoney": None,
            "WinRate": None,
            "PlaceRate": None
        })
    return runners

def parse_all_forms(text, filename="UNKNOWN"):
    lines = text.splitlines()
    race_blocks = []
    current_block = []
    race_number = 1
    box_count = 0
    in_race = False

    for line in lines:
        if re.match(r"^\s*1\.\s", line):
            if current_block:
                race_blocks.append((race_number, "\n".join(current_block)))
                race_number += 1
                current_block = []
            in_race = True
            box_count = 1
            current_block.append(line)
        elif in_race and re.match(r"^\s*[2-9|10]\.\s", line):
            box_count += 1
            current_block.append(line)
            if box_count >= 8:
                in_race = False
        elif in_race:
            current_block.append(line)

    if current_block:
        race_blocks.append((race_number, "\n".join(current_block)))

    all_data = []
    for race_num, block in race_blocks:
        if not is_greyhound_race(block):
            continue
        metadata = extract_race_metadata(block, race_num, filename)
        runners = extract_runners(block)
        for runner in runners:
            runner.update(metadata)
            all_data.append(runner)

    return pd.DataFrame(all_data)
