from linkedin_api import Linkedin
import os
from dotenv import load_dotenv
import json

load_dotenv('.env')
accs = os.getenv('LINKEDIN_ACCOUNTS').split(',')
u, p = accs[0].split(':')

api = Linkedin(u, p)
try:
    res = api.get_company_updates('home-office-vagas-remotas', max_results=2)
    print(json.dumps(res, indent=2))
except Exception as e:
    print(e)
