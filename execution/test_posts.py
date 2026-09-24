import os
from dotenv import load_dotenv
from linkedin_api import Linkedin
import urllib.parse
import json

load_dotenv()
api = Linkedin(os.getenv('LINKEDIN_USER'), os.getenv('LINKEDIN_PASS'))

# Try to fetch posts containing "vaga web designer"
kw = "vaga web designer"
print(f"Searching posts for: {kw}")

# Using native api.search if possible or custom voyager fetch
# Post search URL is usually /search/blended?count=10&filters=List(resultType-%3ECONTENT)&keywords=vaga%20web%20designer&origin=GLOBAL_SEARCH_HEADER&q=all
try:
    params = {
        "count": 10,
        "filters": "List(resultType->CONTENT)",
        "keywords": kw,
        "origin": "GLOBAL_SEARCH_HEADER",
        "q": "all",
        "start": 0
    }
    qs = urllib.parse.urlencode(params, safe='(),->')
    res = api._fetch(f"/search/blended?{qs}")
    data = res.json()
    
    with open("posts_test.json", "w") as f:
        json.dump(data, f, indent=2)
        
    elements = data.get("elements", [])
    print(f"Found {len(elements)} blended elements")
except Exception as e:
    print(f"Error: {e}")
