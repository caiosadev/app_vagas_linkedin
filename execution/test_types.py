import os
import json
from dotenv import load_dotenv
from linkedin_api import Linkedin
from urllib.parse import urlencode

load_dotenv()
api = Linkedin(os.getenv('LINKEDIN_USER'), os.getenv('LINKEDIN_PASS'))
query_str = "(origin:JOB_SEARCH_PAGE_QUERY_EXPANSION,keywords:webdesign,locationFallback:Brazil,selectedFilters:(workplaceType:List(2),timePostedRange:List(r86400)))"
params = {
    "decorationId": "com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-174",
    "count": 50,
    "q": "jobSearch",
    "query": query_str,
    "start": 0,
}
res = api._fetch(
    f"/voyagerJobsDashJobCards?{urlencode(params, safe='(),:')}",
    headers={"accept": "application/vnd.linkedin.normalized+json+2.1"},
)
print(json.dumps(res.json(), indent=2)[:1000])
