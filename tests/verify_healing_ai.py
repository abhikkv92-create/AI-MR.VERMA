import asyncio
import sys
import os
import json
from datetime import datetime

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.platform_cluster import ProductionOrchestrator
    from core.env_manager import load_env_file
    load_env_file(".env")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def test_self_healing():
    print("\n--- Testing Self-Healing Analysis (Isolated) ---")
    orchestrator = ProductionOrchestrator()
    
    # Simulate a failure in audit.log
    log_file = "logs/audit.log"
    os.makedirs("logs", exist_ok=True)
    
    dummy_fail = {
        "timestamp": datetime.now().isoformat(),
        "event": "TASK_FAIL",
        "agent": "DataScientist",
        "error": "ModuleNotFoundError: No module named 'scipy'",
        "context": "Attempting to run statistical analysis on cluster A"
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(dummy_fail) + "\n")
    
    print("Simulated failure injected into audit.log")
    
    result = await orchestrator.trigger_self_heal()
    print("Self-Healing Result:", json.dumps(result, indent=2))
    
    if result.get("status") == "Self-Healing Analysis Complete":
        print("\n[VERIFIED] AI analysis successful.")
        analysis = result.get("analysis", {})
        print(f"Root Cause: {analysis.get('root_cause')}")
        print(f"Remediation: {analysis.get('remediation')}")
    else:
        print("\n[FAILED] AI analysis incomplete.")

if __name__ == "__main__":
    asyncio.run(test_self_healing())
