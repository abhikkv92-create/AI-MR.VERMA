import os
import sys
import asyncio
from core.ai.primary_engine import PrimaryAIEngine
from core.env_manager import load_env_file

async def run_test_suite():
    print("🧪 [PHASE: TEST_RUNNER] Orchestrating Neural Stress Tests...")
    load_env_file("e:/ABHINAV/MR.VERMA/.env")
    engine = PrimaryAIEngine()
    
    # AI identifies which tests to run or generate
    prompt = "Identify 3 critical edge cases for the SupremeOrchestrator and generate high-level test logic. Use [POWERUSEAGE Level 3]."
    res = engine.generate([{"role": "user", "content": prompt}], stream=False)
    print("\n--- AI TEST PLAN ---\n")
    print(res.choices[0].message.content)

if __name__ == "__main__":
    asyncio.run(run_test_suite())
