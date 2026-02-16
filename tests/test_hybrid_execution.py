
import asyncio
import os
import sys
import time
import logging
from concurrent.futures import as_completed

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.processing_unit import kernel_pu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Test.HybridExecution")

def heavy_computation(n):
    """Simulates a CPU-heavy task."""
    res = 0
    for i in range(n):
        res += i * i
    return res

async def test_hybrid_throughput():
    print("\n--- Testing Hybrid P/E Core Throughput ---")
    
    # 1. High Priority (Targets P-Cores: 12 threads)
    print("Spawning 12 High-Priority Tasks (P-Cores)...")
    start = time.time()
    hi_futures = [kernel_pu.submit_task(heavy_computation, priority="high", n=10**7) for _ in range(12)]
    
    # 2. Standard Priority (Targets E-Cores: 8 threads)
    print("Spawning 8 Standard-Priority Tasks (E-Cores)...")
    std_futures = [kernel_pu.submit_task(heavy_computation, priority="standard", n=10**7) for _ in range(8)]
    
    # Wait for all
    print("Waiting for all 20 threads to complete...")
    for f in as_completed(hi_futures + std_futures):
        f.result()
        
    duration = time.time() - start
    print(f"Hybrid Stress Test Complete in {duration:.4f} seconds.")
    print(f"Average throughput: {20 / duration:.2f} tasks/sec across 20 threads.")
    
    # 3. Memory Health Check
    health = kernel_pu.check_system_health()
    print(f"Post-Stress Health: {health['status']} | Available RAM: {health['memory_available_gb']} GB")

if __name__ == "__main__":
    asyncio.run(test_hybrid_throughput())
