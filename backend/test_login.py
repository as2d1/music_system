
import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def test_flow():
    # 1. Login
    print("Attempting login...")
    login_data = {
        'username': 'JX',
        'password': '123456'
    }
    try:
        resp = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        print(f"Login Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return

        data = resp.json()
        token = data.get('token')
        print(f"Token received: {token[:20]}...")

        # 2. Access Songs
        print("\nAttempting to fetch songs...")
        headers = {
            'Authorization': f'Bearer {token}'
        }
        resp = requests.get(f'{BASE_URL}/songs/', headers=headers)
        print(f"Songs Status: {resp.status_code}")
        print(f"Songs Response: {resp.text[:100]}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_flow()
