
import asyncio
import logging
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import SupremeOrchestrator
from core.env_manager import load_env_file

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Test.SocraticGate")

async def test_gate():
    load_env_file()
    
    logger.info("Initializing Supreme Orchestrator...")
    orchestrator = SupremeOrchestrator()
    
    # Test 1: Vague Request (Should Trigger Clarification or Refinement)
    vague_prompt = "Build a thing"
    logger.info(f"--- Testing Vague Prompt: '{vague_prompt}' ---")
    result_vague = await orchestrator.process_request(vague_prompt)
    logger.info(f"Result: {result_vague}")
    
    # Test 2: Clear Request (Should Pass and Trigger Invoke All)
    clear_prompt = "Check system health"
    logger.info(f"--- Testing Clear Prompt: '{clear_prompt}' ---")
    result_clear = await orchestrator.process_request(clear_prompt)
    logger.info(f"Result: {result_clear}")

if __name__ == "__main__":
    asyncio.run(test_gate())
