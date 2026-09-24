import json

with open('.tmp/raw_dump.json', 'r') as f:
    data = json.load(f)

for item in data:
    if item.get("$type") == "com.linkedin.voyager.dash.jobs.JobPosting":
        print("JobPosting:", json.dumps(item, indent=2))
