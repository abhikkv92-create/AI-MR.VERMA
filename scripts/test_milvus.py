import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory_service import memory_service
import asyncio

async def test_connection():
    print("Testing Milvus Connection...")
    if memory_service.connect():
        print("SUCCESS: Connected to Milvus.")
    else:
        print("FAILURE: Could not connect to Milvus.")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_connection())
