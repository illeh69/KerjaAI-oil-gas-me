"""
Convert all *_Jobs.csv files into a single assets/data/jobs.json for the mobile app.

Usage:
    python build_jobs_json.py
"""
import csv, os, glob, json

DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(DIR, "..")
OUTPUT = os.path.join(DIR, "assets", "data", "jobs.json")

all_jobs = []
for f in sorted(glob.glob(os.path.join(CSV_DIR, "*_Jobs.csv"))):
    with open(f, "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            all_jobs.append({
                "id": len(all_jobs),
                "country": row.get("Country", ""),
                "company": row.get("Company", ""),
                "title": row.get("Title", ""),
                "category": row.get("Category", ""),
                "location": row.get("Location", ""),
                "date": row.get("Date Posted", ""),
                "link": row.get("Link", ""),
            })

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(all_jobs, f, ensure_ascii=False, indent=2)

print(f"Written {len(all_jobs)} jobs to {OUTPUT}")
