import os
import requests
import json
import logging

# Configuration
API_KEY = "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"
INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Test.Moonshot")

def test_moonshot():
    logger.info("Testing Secondary NVIDIA Key (Moonshot Kimi)...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "moonshotai/kimi-k2.5",
        "messages": [
            {"role": "system", "content": "You are a high-speed logic processor."},
            {"role": "user", "content": "Calculate the factorial of 5 and explain the logic briefly."}
        ],
        "max_tokens": 1024,
        "temperature": 0.1,
        "stream": False
    }
    
    try:
        response = requests.post(INVOKE_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            logger.info("✅ SUCCESS: Secondary Key is Active")
            logger.info(f"Response: {response.json()['choices'][0]['message']['content']}")
            return True
        else:
            logger.error(f"❌ FAILED: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_moonshot()
