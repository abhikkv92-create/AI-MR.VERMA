import asyncio
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.frontend_cluster import UIDesigner
    from core.env_manager import load_env_file as load_env
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)

async def test_design_muse():
    try:
        # Load secrets
        load_env()
        
        print("--- Testing DesignMuse (AI Layout Gen) with UIDesigner ---")
        agent = UIDesigner()
        agent.start()
        
        task_data = {
            "mode": "design_muse",
            "prompt": "Modern Hero Section for a SaaS AI Platform with a dark theme, large headline, and two call-to-action buttons."
        }
        
        result = await agent.process_task(task_data)
        
        print("\n--- Design Result ---")
        print(result)
        
        if result.get("status") == "DesignMuse Generated":
            design = result.get("design", "")
            if "component_name" in design and "tailwind_classes_used" in design:
                 print("PASS: AI generated a structured design.")
            else:
                 print("PASS (Weak): AI ran but response structure might be invalid.")
        else:
            print(f"FAIL: Status is {result.get('status')}")
            
    except Exception as e:
        print(f"EXECUTION ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_design_muse())
