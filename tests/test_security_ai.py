import asyncio
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.platform_cluster import SecurityArchitect
    from core.env_manager import load_env_file as load_env
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)

async def test_security_scan():
    try:
        # Load secrets
        load_env()
        
        print("--- Testing AI Security Scan with SecurityArchitect ---")
        agent = SecurityArchitect()
        agent.start()
        
        # Create a dummy vulnerable file
        dummy_file = "tests/vulnerable_script.py"
        with open(dummy_file, "w") as f:
            f.write("import os\n")
            f.write("# This is a bad practice example\n")
            f.write("AWS_SECRET_KEY = 'AKIA1234567890'\n")
            f.write("DB_PASSWORD = 'password123'\n")
            f.write("def connect():\n")
            f.write("    os.system(f'mysql -u root -p{DB_PASSWORD}')\n")
        
        task_data = {
            "mode": "ai_security_scan",
            "target_file": dummy_file
        }
        
        result = await agent.process_task(task_data)
        
        print("\n--- Scan Result ---")
        print(result)
        
        # Cleanup
        if os.path.exists(dummy_file):
            os.remove(dummy_file)
        
        if result.get("status") == "AI Security Scan Complete":
            analysis = result.get("analysis", "")
            if "risk_score" in analysis or "critical_vulnerabilities" in analysis:
                 print("PASS: AI detected vulnerabilities.")
            else:
                 print("PASS (Weak): AI ran but response might be generic.")
        else:
            print(f"FAIL: Status is {result.get('status')}")
            
    except Exception as e:
        print(f"EXECUTION ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_security_scan())
