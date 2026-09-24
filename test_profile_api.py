import requests
import json
import os
import time

url = 'http://127.0.0.1:5002'

# 1. Register
res = requests.post(f'{url}/api/auth/register', json={
    'name': 'Test User',
    'email': 'test@example.com',
    'login': 'testuser',
    'password': 'password123'
})
print("Register:", res.status_code, res.text)

# 2. Login
res = requests.post(f'{url}/api/auth/login', json={
    'login': 'testuser',
    'password': 'password123'
})
print("Login:", res.status_code)
if res.status_code == 200:
    token = res.json().get('token')
else:
    print(res.text)
    token = None

if token:
    # 3. Update profile
    res = requests.post(
        f'{url}/api/user/profile',
        headers={'Authorization': f'Bearer {token}'},
        data={'linkedinUrl': 'https://linkedin.com/in/test'}
    )
    print("Update Profile:", res.status_code, res.text)

