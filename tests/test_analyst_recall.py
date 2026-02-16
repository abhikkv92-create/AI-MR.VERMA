
import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.intelligence_cluster import ResearchAnalyst
from core.memory_service import memory_service

logging.basicConfig(level=logging.INFO)

async def test_ra_recall():
    load_dotenv()
    if not memory_service.connect():
        print("Failed to connect to Milvus")
        return
        
    ra = ResearchAnalyst()
    
    # Test 1: Recall Phase 12 info
    print("\n--- Test 1: Recall Phase 12 Details ---")
    res = await ra._execute_task_logic({
        "mode": "recall",
        "query": "What was achieved in Phase 12?"
    })
    
    print(f"Status: {res['status']}")
    for i, mem in enumerate(res['memories']):
        print(f"Result {i+1} from {os.path.basename(mem['metadata'].get('source', 'unknown'))}:")
        print(f"Content: {mem['content'][:150]}...")

if __name__ == "__main__":
    asyncio.run(test_ra_recall())
