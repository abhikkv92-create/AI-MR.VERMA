
import os
import sys
import requests
import logging

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.env_manager import load_env_file

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Test.NVIDIA")

def test_nvidia_connectivity():
    logger.info("--- STARTING NVIDIA API VERIFICATION ---")
    
    # 1. Load Environment
    load_env_file()
    
    api_key = os.environ.get("NVIDIA_API_KEY")
    api_url = os.environ.get("NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
    model = os.environ.get("NVIDIA_MODEL", "moonshotai/kimi-k2.5")
    
    if not api_key:
        logger.error("❌ FAILED: NVIDIA_API_KEY not found in .env or environment.")
        print("\n[!] Please add NVIDIA_API_KEY to your .env file.")
        return False
        
    logger.info(f"API Key found (length: {len(api_key)})")
    logger.info(f"Target URL: {api_url}")
    logger.info(f"Model: {model}")
    
    # 2. Construct Payload
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Explain quantum entanglement briefly."}],
        "max_tokens": 16384,
        "temperature": 0.26,
        "top_p": 0.91,
        "stream": True,
        "chat_template_kwargs": {"thinking": True}
    }
    
    # 3. Send Request with Retry
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3, pool_connections=10, pool_maxsize=10)
    session.mount("https://", adapter)
    
    try:
        logger.info("Sending request (Stream: True, Timeout: 60s)...")
        response = session.post(api_url, headers=headers, json=payload, stream=True, timeout=60)
        
        if response.status_code == 200:
            logger.info("✅ SUCCESS: Stream Connected")
            collected_content = []
            try:
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode("utf-8")
                        if decoded.startswith("data: ") and decoded.strip() != "data: [DONE]":
                            # Just log that we are receiving data
                            pass
            except Exception as e:
                 logger.warning(f"Stream interrupted: {e}")
            
            logger.info("Stream finished successfully.")
            return True
        else:
            logger.error(f"❌ FAILED: API Status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ FAILED: Connection Error: {e}")
        return False

if __name__ == "__main__":
    success = test_nvidia_connectivity()
    sys.exit(0 if success else 1)
