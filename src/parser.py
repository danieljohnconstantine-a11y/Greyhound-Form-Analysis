import re
import pandas as pd
from datetime import datetime

def is_greyhound_race(block):
    return any(name in block for name in ["FERNANDO BALE", "ZAMBORA BROCKIE", "KOBLENZ", "KEEPING", "ASTON"])

def extract_race_metadata(block, race_number):
    date_match = re.search(r"(\d{2}/\d{2}/\d{4})", block)
    track_match = re.search(r"([A-Z][a-z]+)\s+Race\s+\d+", block)
    distance_match = re.search(r"(\d{3,4}m)", block)
    class_match = re.search(r"Grade\s+(\d+)", block)
    weather_match = re.search(r"Weather[:\s]+(\w+)", block)
    surface_match = re.search(r"Surface[:\s]+([\w\s]+)", block)

    return {
        "RaceDate": datetime.strptime(date_match.group(1), "%d/%m/%Y").strftime("%Y-%m-%d") if date_match else "",
        "Track": track_match.group(1) if track_match else "",
        "RaceNumber": str(race_number),
        "Distance": distance_match.group(1) if distance_match else "",
        "Class": class_match.group(1) if class_match else "",
        "Weather": weather_match.group(1) if weather_match else "",
        "Surface": surface_match.group(1) if surface_match else ""
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

def parse_all_forms(text):
    lines = text.splitlines()
    race_blocks = []
    current_block = []
    race_number = 0

    for line in lines:
        if re.match(r"^\s*Race\s+\d+", line, re.IGNORECASE):
            if current_block:
                race_blocks.append((race_number, "\n".join(current_block)))
                current_block = []
            race_number += 1
        current_block.append(line)

    if current_block:
        race_blocks.append((race_number + 1, "\n".join(current_block)))

    all_data = []
    for race_num, block in race_blocks:
        if not is_greyhound_race(block):
            continue
        metadata = extract_race_metadata(block, race_num)
        runners = extract_runners(block)
        for runner in runners:
            runner.update(metadata)
            all_data.append(runner)

    return pd.DataFrame(all_data)
