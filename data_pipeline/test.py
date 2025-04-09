import requests
import time
i=1
while True:
    try:
        response = requests.get("http://localhost:5000/data", timeout=2)
        print(f"Status of {i}: {response.status_code}")
        i+=1
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    time.sleep(2)
