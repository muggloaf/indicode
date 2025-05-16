import requests
import json

def test_transliteration_api():
    url = "http://127.0.0.1:5000/transliterate"
    data = {
        "input_text": "नमस्ते",
        "language": "hindi"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        print(f"Sending request to {url}")
        response = requests.post(url, data=data, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            print(f"Response content: {response.text}")
            try:
                json_response = response.json()
                print(f"Parsed JSON: {json.dumps(json_response, indent=2)}")
                if "output" in json_response:
                    print(f"Transliteration result: {json_response['output']}")
            except json.JSONDecodeError:
                print("Could not parse response as JSON")
        else:
            print(f"Error response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Installing requests package...")
        import sys
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    test_transliteration_api()
