import os
import json
from dotenv import load_dotenv
from linkedin_api import Linkedin
from urllib.parse import urlencode

load_dotenv()
api = Linkedin(os.getenv('LINKEDIN_USER'), os.getenv('LINKEDIN_PASS'))
params = {
    "decorationId": "com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-174",
    "count": 2,
    "q": "jobSearch",
    "query": "(origin:JOB_SEARCH_PAGE_QUERY_EXPANSION,keywords:Webdesigner,locationFallback:Brazil)",
    "start": 0,
}
res = api._fetch(
    f"/voyagerJobsDashJobCards?{urlencode(params, safe='(),:')}",
    headers={"accept": "application/vnd.linkedin.normalized+json+2.1"},
)
data = res.json()
print(json.dumps(data.get("included", [])[:15], indent=2))
