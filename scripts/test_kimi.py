import os
import sys
import asyncio
import json

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai.secondary_engine import SecondaryAIEngine
from core.env_manager import load_env_file

async def run_test():
    load_env_file("e:/ABHINAV/MR.VERMA/.env")
    engine = SecondaryAIEngine()
    if not engine.is_available():
        print("ERROR: Kimi K2.5 Engine not available.")
        return

    print("\n[TEST START] Consulting Kimi K2.5 with minimal prompt...\n")
    response = engine.generate("Say 'KIMI ACTIVE'.", system_prompt="Test.", stream=False, max_tokens=10)
    
    if response:
        print(f"RESPONSE: {response}")
    else:
        print("ERROR: Kimi failed minimal test.")

if __name__ == "__main__":
    asyncio.run(run_test())
