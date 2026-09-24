import sys
import os
from dotenv import load_dotenv

env_path = os.path.abspath('/Users/visuals/Downloads/app-linkedin/.env')
load_dotenv(env_path)

print("SMTP_HOST from env:", os.environ.get('SMTP_HOST'))

sys.path.append(os.path.abspath('/Users/visuals/Downloads/app-linkedin/execution'))
from server import send_newsletter

print("Iniciando disparo manual de teste...")

import execution.server
original_get_db = execution.server.get_newsletter_db_connection

def mock_get_db():
    conn = original_get_db()
    class MockConn:
        def execute(self, query, params):
            res = conn.execute(query, params).fetchall()
            return type('MockRes', (), {'fetchall': lambda: [r for r in res if 'gmail.com' in r['email']]})()
        def close(self):
            conn.close()
    return MockConn()

execution.server.get_newsletter_db_connection = mock_get_db

send_newsletter('3x')
print("Concluído!")
