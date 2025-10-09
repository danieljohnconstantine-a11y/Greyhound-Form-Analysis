import re
import pandas as pd
from datetime import datetime

def extract_race_metadata(block, race_number, filename):
    date_match = re.search(r"(\d{2}/\d{2}/\d{4})", block)
    date_str = ""
    if date_match:
        try:
            date_str = datetime.strptime(date_match.group(1), "%d/%m/%Y").strftime("%Y-%m-%d")
        except:
            date_str = ""

    track_match = re.match(r"([A-Z]{3,})G\d{4}", filename)
    track = track_match.group(1) if track_match else "UNKNOWN"

    distance_match = re.search(r"(\d{3,4})m", block)
    distance = int(distance_match.group(1)) if distance_match else None

    return {
        "RaceDate": date_str,
        "Track": track,
        "RaceNumber": str(race_number),
        "Distance": distance,
        "Class": "",
        "Weather": "",
        "Surface": ""
    }

def extract_runners(block, metadata):
    pattern = r"(\d+)\.\s+([A-Z][A-Za-z\s\-']+).*?Trainer[:\s]+([A-Za-z\s\-']+)"
    matches = re.findall(pattern, block, re.DOTALL)
    runners = []
    for m in matches:
        box = int(m[0])
        dog = m[1].strip()
        trainer = m[2].strip()

        # Simulated last run date and time (replace with real extraction logic)
        last_run_date = "2025-10-03"
        last_run_time = 24.5  # seconds

        # Compute derived features
        try:
            race_date = datetime.strptime(metadata["RaceDate"], "%Y-%m-%d")
            last_date = datetime.strptime(last_run_date, "%Y-%m-%d")
            days_since_last_run = (race_date - last_date).days
        except:
            days_since_last_run = None

        try:
            speed_kmh = round(metadata["Distance"] / last_run_time * 3.6, 2) if metadata["Distance"] and last_run_time else None
        except:
            speed_kmh = None

        # Simulated specialist and experience flags
        distance_specialist = True if metadata["Distance"] and metadata["Distance"] in [300, 400, 450] else False
        track_experience_count = 2 if metadata["Track"] in ["MEAD", "GAWL", "MTG"] else 0

        runners.append({
            "DogName": dog,
            "Box": box,
            "Trainer": trainer,
            "PrizeMoney": None,
            "WinRate": None,
            "PlaceRate": None,
            "LastRunDate": last_run_date,
            "LastRunTime": last_run_time,
            "DaysSinceLastRun": days_since_last_run,
            "SpeedKMH": speed_kmh,
            "DistanceSpecialist": distance_specialist,
            "TrackExperienceCount": track_experience_count,
            **metadata
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
        metadata = extract_race_metadata(block, race_num, filename)
        runners = extract_runners(block, metadata)
        all_data.extend(runners)

    return pd.DataFrame(all_data)
