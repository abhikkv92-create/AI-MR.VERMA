import asyncio
import sys
import os
import json
from datetime import datetime

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.platform_cluster import ProductionOrchestrator
    from core import global_task_queue
    from core.env_manager import load_env_file

    load_env_file(".env")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)


async def test_fix_and_heal():
    print("\n--- Testing 'Fix and Heal' Active Remediation ---")
    orchestrator = ProductionOrchestrator()

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    log_file = "logs/audit.log"

    # 1. Simulate a failure that requires a simple mkdir
    # We use a failure that the AI will likely suggest 'mkdir' for.
    test_dir = "temp_remediation_dir"
    if os.path.exists(test_dir):
        import shutil

        shutil.rmtree(test_dir)

    dummy_fail = {
        "timestamp": datetime.now().isoformat(),
        "event": "TASK_FAIL",
        "agent": "DataScientist",
        "error": f"FileNotFoundError: Required directory '{test_dir}' is missing",
        "context": "Initializing local work buffer",
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(dummy_fail) + "\n")

    print(f"Injected failure: Missing directory '{test_dir}'")

    # 2. Start Task Queue (since trigger_self_heal enqueues the healing task)
    await global_task_queue.start()

    # 3. Trigger self-heal with auto_heal=True
    print("Triggering self-healing analysis and execution...")
    # Mode 'self_heal' will call trigger_self_heal
    result = await orchestrator._execute_task_logic(
        {"mode": "self_heal", "auto_heal": True}
    )

    print("Analysis Result:", json.dumps(result, indent=2))

    if result.get("status") == "Self-Healing Analysis Complete":
        print("Analysis successful. Waiting for background healing task to execute...")

        # Wait up to 30s for the background task to finish
        for _ in range(30):
            await asyncio.sleep(1)
            if os.path.exists(test_dir):
                print(
                    f"SUCCESS: Directory '{test_dir}' was created by autonomous remediation!"
                )

                # Check audit.log for HEAL_ACTION
                with open(log_file, "r") as f:
                    content = f.read()
                    if '"event": "HEAL_ACTION"' in content:
                        print("Verified: HEAL_ACTION recorded in audit.log")
                    else:
                        print("WARNING: HEAL_ACTION not found in audit.log yet.")
                break
        else:
            print("FAIL: Remediation directory not found after timeout.")
    else:
        print(f"FAIL: Self-healing analysis failed with status: {result.get('status')}")

    await global_task_queue.stop()


if __name__ == "__main__":
    asyncio.run(test_fix_and_heal())
