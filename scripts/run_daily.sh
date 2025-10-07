#!/bin/bash
# Example wrapper: parse PDFs for a date and generate picks
DATE=${1:-$(date +%F)}
echo "Processing date: $DATE"
python3 pipeline/parse_forms.py --date "$DATE"
python3 analysis/predict.py --date "$DATE" --top 1
echo "Done. Picks are in out/picks_${DATE}.csv"
