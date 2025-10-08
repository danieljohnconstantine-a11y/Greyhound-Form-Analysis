import re
import pandas as pd
from datetime import datetime

def is_greyhound_race(text):
    clues = [
        r"\bFERNANDO BALE\b", r"\bZAMBORA BROCKIE\b", r"\bKOBLENZ\b",
        r"\bBox History\b", r"\bBP\b", r"\bMDN\b", r"\bRST WIN\b",
        r"\bTrack Direction\b", r"\bAnti-Clockwise\b",
        r"\bDistance: (3\d{2}|4\d{2}|5\d{2})m\b"
    ]
    return any(re.search(clue, text, re.IGNORECASE) for clue in clues)

def extract_race_metadata(block):
    date_match = re.search(r"(\d{2}/\d{2}/\d{4})", block)
    track_match = re.search(r"([A-Z][a-z]+)\s+Race\s+\d+", block)
    race_match = re.search(r"Race\s+No\s+(\d+)", block)
    distance_match = re.search(r"Distance:\s+(\d+m)", block)
    class_match = re.search(r"Class:\s+(\w+)", block)
    weather_match = re.search(r"Weather:\s+(\w+)", block)
    surface_match = re.search(r"Surface:\s+([\w\s]+)", block)

    return {
        "RaceDate": datetime.strptime(date_match.group(1), "%d/%m/%Y").strftime("%Y-%m-%d") if date_match else "",
        "Track": track_match.group(1) if track_match else "",
        "RaceNumber": race_match.group(1) if race_match else "",
        "Distance": distance_match.group(1) if distance_match else "",
        "Class": class_match.group(1) if class_match else "",
        "Weather": weather_match.group(1) if weather_match else "",
        "Surface": surface_match.group(1) if surface_match else ""
    }

def extract_runners(block):
    pattern = r"(\d+)\n([A-Z][A-Za-z\s\-']+)\s+\((\d+)\).*?Trainer:\s+([A-Za-z\s\-']+).*?Prize Money:\s+\$(\d+).*?Win / Place:\s+(\d+%) / (\d+%)"
    matches = re.findall(pattern, block, re.DOTALL)
    runners = []
    for m in matches:
        runners.append({
            "DogName": m[1].strip(),
            "Box": int(m[2]),
            "Trainer": m[3].strip(),
            "PrizeMoney": int(m[4]),
            "WinRate": m[5],
            "PlaceRate": m[6]
        })
    return runners

def parse_all_races(text):
    race_blocks = re.split(r"Race\s+No\s+\d+", text)
    all_data = []

    for block in race_blocks:
        if not is_greyhound_race(block):
            continue

        metadata = extract_race_metadata(block)
        runners = extract_runners(block)

        for runner in runners:
            runner.update(metadata)
            all_data.append(runner)

    return pd.DataFrame(all_data)

if __name__ == "__main__":
    with open("BDGOG0810form.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    df = parse_all_races(raw_text)

    if not df.empty:
        df.to_csv("parsed_race_form.csv", index=False)
        print("✅ All greyhound races parsed and saved to parsed_race_form.csv")
    else:
        print("🚫 No greyhound races detected in this file.")
