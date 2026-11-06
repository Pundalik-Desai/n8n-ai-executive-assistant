import os
import requests
import json

user_message = "Can you tell me about black holes in 3-4 lines"

request_message = {"message": user_message}

url = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/1f775159-453d-4b8d-9674-91979537ecf9")

print(f"Sending request to: {url}")
print(f"Payload: {request_message}\n")

response = requests.post(url, json=request_message)

print(f"Status Code: {response.status_code}")

try:
    data = response.json()
    print("\n--- Response JSON ---")
    print(json.dumps(data, indent=2))
    
    # Try extracting output
    print("\n--- Extracted Output ---")
    if isinstance(data, list) and len(data) > 0 and "output" in data[0]:
        print(data[0]["output"])
    elif isinstance(data, dict) and "output" in data:
        print(data["output"])
    elif isinstance(data, dict) and "text" in data:
        print(data["text"])
    else:
        print(data)
except Exception:
    print("\n--- Raw Response Text ---")
    print(response.text)
