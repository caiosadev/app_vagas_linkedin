from linkedin_api import Linkedin
import os
from dotenv import load_dotenv

load_dotenv('.env')
accs = os.getenv('LINKEDIN_ACCOUNTS').split(',')
u, p = accs[0].split(':')

api = Linkedin(u, p)
try:
    res = api.get_company_updates('home-office-vagas-remotas', max_results=5)
    print("Company updates fetched:", len(res))
    
    # Tentando groups
    # As url para grupo feed é /feed/updates?q=highlightedFeedForGroups&highlightedUpdateUrn... ou algo assim?
    # No prompt o usuario colocou: /groups/4497931/?q=highlightedFeedForGroups
    # Talvez a API do voyager tenha um group feed endpoint.
    res_grp = api._fetch('/groups/4497931/feed')
    print("Group fetch:", res_grp.status_code)
except Exception as e:
    print(e)
