
import asyncio
import logging
import sys
import os
import json

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.intelligence_cluster import ResearchAnalyst
from core.env_manager import load_env_file

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Test.AIAnalyst")

async def test_analyst():
    load_env_file()
    
    logger.info("Initializing Research Analyst...")
    analyst = ResearchAnalyst()
    analyst.start()
    
    # Target core directory for analysis
    target_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core")
    
    logger.info(f"--- Testing Deep AI Analysis on {target_dir} ---")
    result = await analyst.process_task({"mode": "deep_ai", "target_dir": target_dir})
    
    logger.info("--- Analysis Result ---")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_analyst())
