import requests
import json

url = "http://127.0.0.1:8000/api/match-profile"
data = {"text": "Saya ingin menjadi programmer python", "top_k": 3}

try:
    print("Testing match-profile...")
    resp = requests.post(url, json=data)
    print(f"Status: {resp.status_code}")
    print(resp.json())
except Exception as e:
    print(f"Error: {e}")
