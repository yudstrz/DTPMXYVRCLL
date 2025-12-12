import requests
import json
import os
import sys

# Load env to get key (manual check)
def get_key():
    try:
        with open('.env.local', 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    return line.strip().split('=', 1)[1]
    except:
        return None

GEMINI_KEY = get_key()
print(f"Loaded Key from .env.local: {GEMINI_KEY[:10]}..." if GEMINI_KEY else "Key not found")

def test_chat():
    print("\n--- Testing Chat API ---")
    url = "http://127.0.0.1:8000/api/chat"
    payload = {
        "message": "Halo, apa kabar?",
        "history": []
    }
    try:
        resp = requests.post(url, json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
    except Exception as e:
        print(f"Chat Error: {e}")

def test_match():
    print("\n--- Testing Match API ---")
    url = "http://127.0.0.1:8000/api/match-profile"
    payload = {
        "text": "Saya ingin menjadi data scientist python",
        "top_k": 3
    }
    try:
        resp = requests.post(url, json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
    except Exception as e:
        print(f"Match Error: {e}")

def check_vectors():
    print("\n--- Checking Data Integrity ---")
    pon_path = os.path.join('data', 'pon_vectors.json')
    if not os.path.exists(pon_path):
        print(f"[FAIL] {pon_path} does not exist!")
        return
    
    try:
        with open(pon_path, 'r') as f:
            data = json.load(f)
            print(f"Vector Count: {len(data)}")
            if len(data) > 0:
                print(f"First Vector Sample (first 5 dims): {data[0][:5]}")
                zeros = sum(1 for x in data[0] if x == 0)
                print(f"Zeros in first vector: {zeros}/{len(data[0])}")
            else:
                print("[WARN] Vector list is empty")
    except Exception as e:
        print(f"[FAIL] Error reading vectors: {e}")

if __name__ == "__main__":
    check_vectors()
    test_chat()
    test_match()
