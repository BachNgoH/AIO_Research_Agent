import requests
import json
from datetime import time


# Base URL (replace with your actual API URL)
base_url = "http://127.0.0.1:8004/v1"  # Example: localhost

# 1. Test /complete endpoint
# complete_url = f"{base_url}/complete"
# message_data = {"message": "Hello from my script!"}
# response = requests.post(complete_url, json=message_data)

# if response.status_code == 200:
#     print("'/complete' response:", response.json())
# else:
#     print(f"Error calling '/complete': {response.status_code} - {response.text}")

# 2. Test /schedule/update (valid)
update_url = f"{base_url}/schedule/update"
new_time = "21:00"
time_data = {"new_time": new_time}
response = requests.post(update_url, json=time_data)

if response.status_code == 200:
    print("'/schedule/update' (valid) response:", response.json())
else:
    print(f"Error calling '/schedule/update': {response.status_code} - {response.text}")

# 3. Test /schedule/update (invalid)
invalid_time_data = {"new_time": "not a valid time"}
response = requests.post(update_url, json=invalid_time_data)

if response.status_code == 200:  
    print("'/schedule/update' (invalid) response:", response.json())
else:
    print(f"Error calling '/schedule/update': {response.status_code} - {response.text}")
    
# 4. Test /schedule endpoint
schedule_url = f"{base_url}/schedule"
response = requests.get(schedule_url)

if response.status_code == 200:
    print("'/schedule' response:", response.json())
else:
    print(f"Error calling '/schedule': {response.status_code} - {response.text}")