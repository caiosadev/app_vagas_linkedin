import os
from dotenv import load_dotenv
from linkedin_api import Linkedin

load_dotenv()
try:
    api = Linkedin(os.getenv('LINKEDIN_USER'), os.getenv('LINKEDIN_PASS'))
    profile = api.get_profile('caiosadev')
    print("Profile Output:", profile)
except Exception as e:
    import traceback
    traceback.print_exc()
