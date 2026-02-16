import asyncio
import os
import sys
import time
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai.secondary_engine import SecondaryAIEngine
from agents.intelligence_cluster import ResearchAnalyst, AIMLEngineer

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DualEngine.Test")

async def test_dual_engine():
    logger.info(">>> STARTING DUAL-ENGINE DEEP TEST <<<")
    report = {"primary": None, "secondary": None, "routing": None}
    
    # 1. Environment Check
    logger.info("--- Phase 1: Environment Check ---")
    pri_key = os.environ.get("NVIDIA_API_KEY")
    sec_key = os.environ.get("NVIDIA_API_KEY_SECONDARY")
    
    logger.info(f"Primary Key Present: {bool(pri_key)}")
    logger.info(f"Secondary Key Present: {bool(sec_key)}")
    
    if not sec_key:
        logger.error("❌ CRITICAL: Secondary Key NOT found in environment.")
        return
        
    # 2. Secondary Engine Direct Test
    logger.info("\n--- Phase 2: Secondary Engine Direct Test (Moonshot Kimi) ---")
    engine = SecondaryAIEngine()
    start_t = time.time()
    response = engine.generate("Explain the concept of 'Context Window' in 10 words.", stream=False)
    duration = time.time() - start_t
    
    if response:
        logger.info(f"✅ Secondary Engine Response ({duration:.2f}s): {response}")
        report["secondary"] = "SUCCESS"
    else:
        logger.error("❌ Secondary Engine Failed")
        report["secondary"] = "FAILED"

    # 3. Agent Routing Test (ResearchAnalyst)
    # ResearchAnalyst uses standard requests in _execute_task_logic, patched to use Secondary Key
    logger.info("\n--- Phase 3: Smart Routing Test (ResearchAnalyst) ---")
    
    # We must patch the environment variable for the agent process if not already set globally
    # (Since we injected it via env_manager, it should be there, but let's be safe)
    os.environ["NVIDIA_API_KEY_SECONDARY"] = sec_key
    
    analyst = ResearchAnalyst()
    analyst.is_active = True # Mock activation
    
    # We'll use the 'deep_ai' mode which calls analyze_code_with_ai -> uses secondary key logic
    # We need a dummy python file for it to analyze
    dummy_file = "tests/dummy_target.py"
    with open(dummy_file, "w") as f:
        f.write("def hello():\n    print('Hello World')\n")
        
    try:
        # Mocking task data
        task_payload = {
            "mode": "deep_ai",
            "target_dir": "tests" # Point to where dummy_target.py is
        }
        
        logger.info("Invoking ResearchAnalyst (Should use Kimi-k2.5)...")
        start_t = time.time()
        result = await analyst._execute_task_logic(task_payload)
        duration = time.time() - start_t
        
        if result.get("status") == "AI Analysis Complete":
            logger.info(f"✅ Routing Success ({duration:.2f}s)")
            logger.info(f"Analysis Output Snippet: {result['analysis'][:100]}...")
            report["routing"] = "SUCCESS"
        else:
            logger.error(f"❌ Routing Failed: {result}")
            report["routing"] = "FAILED"
            
    except Exception as e:
        logger.error(f"❌ Routing Exception: {e}")
        report["routing"] = "ERROR"
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)

    # 4. Final Summary
    logger.info("\n>>> TEST SUITE COMPLETE <<<")
    logger.info(f"Summary: {report}")
    return report

if __name__ == "__main__":
    asyncio.run(test_dual_engine())
