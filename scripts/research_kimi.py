import os
import sys
import asyncio
import json

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai.secondary_engine import SecondaryAIEngine
from core.env_manager import load_env_file

async def run_research():
    # Load env
    load_env_file("e:/ABHINAV/MR.VERMA/.env")
    
    engine = SecondaryAIEngine()
    if not engine.is_available():
        print("ERROR: Kimi K2.5 Engine not available.")
        return

    research_prompt = (
        "Research 'Quantum-Lite' architectures for AI agents in 2026. "
        "Focus on: \n"
        "1. Neural JIT (Just-In-Time) agent generation\n"
        "2. Ephemeral Swarm patterns (Minimalist runtime)\n"
        "3. Hardware-Native performance (Intel i9 cache-line optimization)\n"
        "4. Semantic Code Shrinking (Zero-boilerplate logic).\n\n"
        "Propose a V4.0 blueprint for MR.VERMA to be 10x faster and 50% lighter. "
        "Use [POWERUSEAGE Level 3]."
    )
    
    system_prompt = "You are the MR.VERMA AI Researcher. Provide a deep, technically rigorous research report."
    
    print("\n[RESEARCH START] Consulting Kimi K2.5...\n")
    
    response = engine.generate(research_prompt, system_prompt=system_prompt, stream=False, max_tokens=2048)
    
    if response:
        print("\n--- RESEARCH FINDINGS ---\n")
        print(response)
        
        # Save to file for synthesis
        with open("e:/ABHINAV/MR.VERMA/logs/research_results.md", "w", encoding="utf-8") as f:
            f.write(response)
        print(f"\n[RESEARCH COMPLETE] Results saved to logs/research_results.md")
    else:
        print("ERROR: Research failed to generate a response.")

if __name__ == "__main__":
    asyncio.run(run_research())
