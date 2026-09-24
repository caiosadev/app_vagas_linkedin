import os
import json
from dotenv import load_dotenv
from linkedin_api import Linkedin

load_dotenv()
api = Linkedin(os.getenv('LINKEDIN_USER'), os.getenv('LINKEDIN_PASS'))
try:
    profile = api.get_profile('caiosadev')
    print("Keys:", profile.keys())
    print("Summary:", profile.get('summary', ''))
    print("Experience:", len(profile.get('experience', [])))
except Exception as e:
    print("Error:", e)
