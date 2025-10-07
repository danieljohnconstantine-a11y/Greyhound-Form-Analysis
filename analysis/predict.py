#!/usr/bin/env python3
"""analysis/predict.py

Load parsed JSON files for a date, run a simple heuristic score (lower last_time better),
and write picks CSV to out/picks_YYYY-MM-DD.csv
"""
import argparse
from pathlib import Path
import json
import csv
from datetime import datetime
from math import inf
import statistics

def iso_date(s):
    if s:
        return s
    return datetime.utcnow().strftime("%Y-%m-%d")

def load_parsed_for_date(date_str):
    p = Path('parsed') / date_str
    files = sorted(p.glob('*.json')) if p.exists() else []
    races = []
    for f in files:
        arr = json.loads(f.read_text(encoding='utf-8'))
        # arr is list of races
        for r in arr:
            # annotate source file
            r['source_file'] = f.name
            races.append(r)
    return races

def score_race(race):
    # simple: prefer runners with numeric last_time (lower better), fallback to 0
    runners = race.get('runners', [])
    scored = []
    for r in runners:
        t = r.get('last_time')
        score = -t if t is not None else -inf  # higher is better for sorting
        scored.append({**r, 'score': score})
    scored_sorted = sorted(scored, key=lambda x: x['score'], reverse=True)
    return scored_sorted

def picks_for_date(date_str, top_n=1):
    races = load_parsed_for_date(date_str)
    picks = []
    for race in races:
        scored = score_race(race)
        if scored:
            for sel in scored[:top_n]:
                picks.append({
                    'date': date_str,
                    'race_no': race.get('race_no'),
                    'track_source': race.get('source_file'),
                    'name': sel.get('name'),
                    'box': sel.get('box'),
                    'score': sel.get('score')
                })
    return picks

def save_picks_csv(picks, date_str):
    out_dir = Path('out')
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f'picks_{date_str}.csv'
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['date','race_no','track_source','name','box','score'])
        writer.writeheader()
        for p in picks:
            writer.writerow(p)
    return path

def main(date=None, top_n=1):
    date = iso_date(date)
    picks = picks_for_date(date, top_n=top_n)
    if not picks:
        print('No picks generated for', date)
        return
    out = save_picks_csv(picks, date)
    print('Picks saved to', out)

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--date', help='YYYY-MM-DD (defaults to today)', default=None)
    p.add_argument('--top', type=int, default=1, help='Top N selections per race')
    args = p.parse_args()
    main(args.date, args.top)
