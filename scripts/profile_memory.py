import sys
import os
import tracemalloc
import logging
import asyncio

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.orchestrator import SupremeOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Profiler")

async def profile_orchestrator(iterations=50):
    tracemalloc.start()
    orchestrator = SupremeOrchestrator()
    await orchestrator.startup()
    
    snapshot1 = tracemalloc.take_snapshot()
    
    logger.info(f"Starting memory profiling for {iterations} iterations...")
    for i in range(iterations):
        await orchestrator.process_request(f"Stress test iteration {i}")
        if i % 10 == 0:
            logger.info(f"Completed {i} iterations")
            
    await orchestrator.shutdown()
    snapshot2 = tracemalloc.take_snapshot()
    
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    logger.info("[ TOP 10 MEMORY DIFFERENCES ]")
    for stat in top_stats[:10]:
        logger.info(stat)

if __name__ == "__main__":
    asyncio.run(profile_orchestrator())
