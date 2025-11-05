import subprocess
import datetime
import os

def run_pipeline():
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"\n📅 Running Greyhound Analytics for {today}...\n")

    result = subprocess.run(["python", "main.py"], capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print("⚠️ Errors:\n", result.stderr)

    for file in ["todays_form.csv", "ranked.csv", "picks.csv"]:
        path = os.path.join("outputs", file)
        if os.path.exists(path):
            print(f"✅ {file} generated.")
        else:
            print(f"❌ {file} missing.")

if __name