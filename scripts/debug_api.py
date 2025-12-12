import requests
import json
import sys

def test_match_profile():
    url = "http://127.0.0.1:8001/api/match-profile"
    payload = {
        "text": "Saya seorang software engineer dengan pengalaman di Python dan React. Saya ingin mencari pekerjaan remote.",
        "top_k": 3
    }
    
    print(f"Testing API: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            with open('debug_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            print("Response saved to debug_response.json")
            
            if "error" in data:
                print("\n[FAIL] API returned an error.")
                return False
            if "recommendations" not in data:
                print("\n[FAIL] 'recommendations' key missing in response.")
                return False
            if len(data["recommendations"]) == 0:
                print("\n[WARN] Recommendations list is empty.")
            else:
                print("\n[SUCCESS] Recommendations received.")
                return True
                
        except json.JSONDecodeError:
            print(f"Raw Response: {response.text}")
            print("\n[FAIL] Response is not valid JSON.")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n[FAIL] Could not connect to API. Is the server running on port 8000?")
        return False
    except Exception as e:
        print(f"\n[FAIL] Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_match_profile()
    if not success:
        sys.exit(1)
