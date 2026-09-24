import os
import json
from dotenv import load_dotenv
from linkedin_api import Linkedin

load_dotenv()
api = Linkedin(os.getenv('LINKEDIN_USER'), os.getenv('LINKEDIN_PASS'))
job = api.get_job('4470979922') # Job ID from the list
print(json.dumps(job, indent=2))
