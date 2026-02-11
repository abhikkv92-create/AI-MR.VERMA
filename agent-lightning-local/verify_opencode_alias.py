import requests
import json

def test_alias():
    url = "http://localhost:8550/v1/chat/completions"
    payload = {
        "model": "opencode/qwen3-coder",
        "messages": [
            {"role": "user", "content": "Hello, explain who you are."}
        ],
        "stream": False
    }
    
    print(f"Testing alias: {payload['model']}")
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            print(f"Response Content: {content[:100]}...")
            if "Verma" in content or "Operator" in content:
                print("✅ Verification Success: Proxy correctly routed to Mr. Verma.")
            else:
                print("⚠️ Verification Partial: Response received but persona not detected.")
        else:
            print(f"❌ Verification Failed: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_alias()
