import asyncio
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.intelligence_cluster import DataScientist
    from core.env_manager import load_env_file as load_env
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)

async def test_log_analysis():
    try:
        # Load secrets
        load_env()
        
        print("--- Testing AI Log Analysis with DataScientist ---")
        agent = DataScientist()
        
        # Create a dummy log file if it doesn't exist
        dummy_log = "logs/test_system.log"
        os.makedirs("logs", exist_ok=True)
        with open(dummy_log, "w") as f:
            f.write("2026-02-13 10:00:00 - Kernel.Main - INFO - System started.\n")
            f.write("2026-02-13 10:05:00 - Agents.Backend - ERROR - Database connection timeout.\n")
            f.write("2026-02-13 10:06:00 - Agents.Backend - WARNING - High memory usage (85%).\n")
            f.write("2026-02-13 10:10:00 - Kernel.Main - INFO - Operation successful.\n")
        
        task_data = {
            "mode": "ai_log_analysis",
            "log_file": dummy_log
        }
        
        agent.start()
        result = await agent.process_task(task_data)
        
        print("\n--- Analysis Result ---")
        print(result)
        
        if result.get("status") == "AI Log Analysis Complete":
            analysis = result.get("analysis", "")
            if "Critical" in analysis or "Warning" in analysis or "issues" in analysis:
                 print("PASS: AI detected issues in log.")
            else:
                 print("PASS (Weak): AI ran but response might be generic.")
        else:
            print(f"FAIL: Status is {result.get('status')}")
            
    except Exception as e:
        print(f"EXECUTION ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_log_analysis())
