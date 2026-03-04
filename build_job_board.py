"""
Build the ME Oil & Gas Job Board HTML from CSV files.

Usage:
    python build_job_board.py

Reads all *_Jobs.csv files in the same folder,
uses job_board_template.html as the template,
and outputs ME_Oil_Gas_Jobs.html.
"""
import csv, os, glob, json
from datetime import date
from collections import defaultdict

DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(DIR, "job_board_template.html")
OUTPUT = os.path.join(DIR, "ME_Oil_Gas_Jobs.html")

# Read all CSV files
all_jobs = []
for f in sorted(glob.glob(os.path.join(DIR, "*_Jobs.csv"))):
    with open(f, "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            all_jobs.append({
                "country": row.get("Country", ""),
                "company": row.get("Company", ""),
                "title": row.get("Title", ""),
                "category": row.get("Category", ""),
                "location": row.get("Location", ""),
                "date": row.get("Date Posted", ""),
                "link": row.get("Link", ""),
            })

# Counts
by_company = defaultdict(int)
by_country = defaultdict(int)
by_category = defaultdict(int)
for j in all_jobs:
    by_company[j["company"]] += 1
    by_country[j["country"]] += 1
    if j["category"]:
        by_category[j["category"]] += 1

companies = sorted(by_company)
countries = sorted(by_country)
categories = sorted(by_category)

# Build option tags
company_opts = "".join(
    f'<option value="{c}">{c} ({by_company[c]})</option>' for c in companies
)
country_opts = "".join(
    f'<option value="{c}">{c} ({by_country[c]})</option>' for c in countries
)
category_opts = "".join(
    f'<option value="{c}">{c} ({by_category[c]})</option>' for c in categories
)

# Read template and fill placeholders
with open(TEMPLATE, "r", encoding="utf-8") as f:
    html = f.read()

replacements = {
    "{{TOTAL_JOBS}}": str(len(all_jobs)),
    "{{TOTAL_COMPANIES}}": str(len(companies)),
    "{{TOTAL_COUNTRIES}}": str(len(countries)),
    "{{LAST_UPDATED}}": date.today().isoformat(),
    "{{COMPANY_OPTIONS}}": company_opts,
    "{{COUNTRY_OPTIONS}}": country_opts,
    "{{CATEGORY_OPTIONS}}": category_opts,
    "{{JOBS_JSON}}": json.dumps(all_jobs, ensure_ascii=False),
}

for placeholder, value in replacements.items():
    html = html.replace(placeholder, value)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Built {OUTPUT}")
print(f"  {len(all_jobs)} jobs | {len(companies)} companies | {len(countries)} countries")
