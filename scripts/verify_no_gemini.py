import requests
import json

def test_match():
    url = "http://localhost:8000/api/match-profile"
    payload = {
        "text": "saya seorang data analyst yang ahli menggunakan python dan sql",
        "top_k": 3
    }
    
    try:
        print(f"Sending request to {url}...")
        resp = requests.post(url, json=payload)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            
            if "recommendations" in data:
                print("\nSUCCESS: Recommendations received!")
            else:
                print("\nWARNING: Unexpected response format.")
        else:
            print(f"\nERROR: API returned {resp.text}")
            
    except Exception as e:
        print(f"\nEXCEPTION: {str(e)}")

if __name__ == "__main__":
    test_match()
