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


async def test_self_healing():
    print("\n--- Testing Self-Healing Analysis ---")
    orchestrator = ProductionOrchestrator()

    # Simulate a failure in audit.log
    log_file = "logs/audit.log"
    os.makedirs("logs", exist_ok=True)

    dummy_fail = {
        "timestamp": datetime.now().isoformat(),
        "event": "TASK_FAIL",
        "agent": "DataScientist",
        "error": "ModuleNotFoundError: No module named 'scipy'",
        "context": "Attempting to run statistical analysis on cluster A",
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(dummy_fail) + "\n")

    print("Simulated failure injected into audit.log")

    result = await orchestrator.trigger_self_heal()
    print("Self-Healing Result:", json.dumps(result, indent=2))

    if result.get("status") == "Self-Healing Analysis Complete":
        print("PASS: AI successfully analyzed the failure.")
    else:
        print("FAIL: AI analysis did not complete as expected.")


async def dummy_bg_task(name, duration):
    print(f"Background task {name} starting (duration: {duration}s)...")
    await asyncio.sleep(duration)
    print(f"Background task {name} finished!")


async def test_task_queue():
    print("\n--- Testing Async Task Queue ---")
    orchestrator = ProductionOrchestrator()

    # Start the queue
    await global_task_queue.start()

    # Enqueue tasks via orchestrator
    await orchestrator.enqueue_background_task(
        "healing_001", dummy_bg_task, "DependencyInstaller", 2
    )
    await orchestrator.enqueue_background_task(
        "cleanup_002", dummy_bg_task, "LogPurger", 1
    )

    print("Tasks enqueued. Waiting for processing...")
    await asyncio.sleep(4)  # Wait for tasks to finish

    stats = global_task_queue.get_stats()
    print("Queue Stats:", json.dumps(stats, indent=2))

    await global_task_queue.stop()

    if stats["tasks_processed"] >= 2:
        print("PASS: TaskQueue processed background tasks successfully.")
    else:
        print("FAIL: TaskQueue did not process tasks as expected.")


async def main():
    await test_self_healing()
    await test_task_queue()


if __name__ == "__main__":
    asyncio.run(main())
