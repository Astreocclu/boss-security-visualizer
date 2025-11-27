import requests
import os
import json

# Configuration
BASE_URL = 'http://localhost:8000'
USERNAME = 'testuser'
PASSWORD = 'password' # Assuming default, if fails we create one
IMAGE_PATH = '/home/reid/Boss Screens/boss-security-visualizer/media/security+window+screens.webp'

def create_test_user():
    # We'll assume user exists or we can't easily create via API without auth
    pass

def get_token():
    url = f"{BASE_URL}/api/auth/login/"
    response = requests.post(url, data={'username': USERNAME, 'password': PASSWORD})
    if response.status_code == 200:
        return response.json()
    print(f"Login failed: {response.status_code} {response.text}")
    return None

def test_create_visualization(access_token):
    url = f"{BASE_URL}/api/visualizations/"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Data matching the frontend request
    data = {
        'screen_categories': json.dumps(['Door']), # Test Door Logic
        'opacity': '95',
        'color': 'Black',
        'mesh_choice': '12x12',
        'frame_color': 'Black',
        'mesh_color': 'Black'
    }
    
    files = {
        'original_image': open(IMAGE_PATH, 'rb')
    }
    
    print(f"Sending request to {url}...")
    response = requests.post(url, headers=headers, data=data, files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("SUCCESS: Visualization request created!")
        request_id = response.json()['id']
        
        # Poll for completion
        import time
        print(f"Polling for completion (Request ID: {request_id})...")
        for _ in range(60): # Wait up to 60 seconds
            status_url = f"{BASE_URL}/api/visualizations/{request_id}/"
            status_res = requests.get(status_url, headers=headers)
            if status_res.status_code == 200:
                status_data = status_res.json()
                status = status_data['status']
                print(f"Status: {status} ({status_data.get('status_message', '')})")
                
                if status == 'complete':
                    print("SUCCESS: Processing completed!")
                    print("Final JSON Response:")
                    print(json.dumps(status_data, indent=2)) # Use status_data here as it's the latest status
                    return True
                elif status == 'failed':
                    print(f"FAILURE: Processing failed. Error: {status_data.get('error_message')}")
                    return False
            time.sleep(2)
            
        print("TIMEOUT: Processing took too long.")
        return False
    else:
        print("FAILURE: Could not create request.")
        return False

if __name__ == "__main__":
    # Ensure image exists
    if not os.path.exists(IMAGE_PATH):
        print(f"Image not found at {IMAGE_PATH}")
        exit(1)

    # Try to login
    tokens = get_token()
    if not tokens:
        # Try registering or just fail
        print("Could not login. Please ensure testuser exists.")
        # We can try to create user via manage.py if needed, but let's see.
        exit(1)
    
    success = test_create_visualization(tokens['access'])
    if success:
        exit(0)
    else:
        exit(1)
