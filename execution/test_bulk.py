import os
import json
from dotenv import load_dotenv
from linkedin_api import Linkedin
from urllib.parse import urlencode

load_dotenv()
api = Linkedin(os.getenv('LINKEDIN_USER'), os.getenv('LINKEDIN_PASS'))

params = {
    "decorationId": "com.linkedin.voyager.dash.deco.jobs.web.shared.WebCompactJobPosting-134",
    "ids": "List(urn:li:fsd_jobPosting:4470979922,urn:li:fsd_jobPosting:4470997011)"
}

try:
    res = api._fetch(f"/voyagerJobsDashJobPostings?{urlencode(params, safe='(),:')}", headers={"accept": "application/vnd.linkedin.normalized+json+2.1"})
    print(json.dumps(res.json(), indent=2)[:1500])
except Exception as e:
    print(e)
