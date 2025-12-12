import requests
import json

url = "http://127.0.0.1:8000/api/chat"
data = {"message": "Hello, are you working?", "history": []}

try:
    print("Testing chat...")
    resp = requests.post(url, json=data)
    print(f"Status: {resp.status_code}")
    print(resp.json())
except Exception as e:
    print(f"Error: {e}")
