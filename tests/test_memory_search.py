
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.memory_service import memory_service

async def test_search():
    load_dotenv()
    if not memory_service.connect():
        print("Failed to connect to Milvus")
        return
        
    query = "remediation steps for self-healing"
    print(f"Searching for: '{query}'")
    results = await memory_service.search(query, limit=3)
    
    if not results:
        print("No results found.")
    else:
        for i, res in enumerate(results):
            print(f"\nResult {i+1} (Score: {res['score']:.4f}):")
            print(f"Source: {res['metadata'].get('source')}")
            print(f"Content snippet: {res['content'][:200]}...")

if __name__ == "__main__":
    asyncio.run(test_search())
