import os
import json
from dotenv import load_dotenv
from linkedin_api import Linkedin

load_dotenv()
api = Linkedin(os.getenv('LINKEDIN_USER'), os.getenv('LINKEDIN_PASS'))
res = api.search_jobs("webdesign", limit=2)
print("Result len:", len(res))
if res:
    print(json.dumps(res[0], indent=2))
