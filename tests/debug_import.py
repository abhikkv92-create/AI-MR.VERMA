import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Step 1: Importing os")
import os
print("Step 2: Importing env_manager")
try:
    from core.env_manager import load_env
    print("Success: env_manager imported")
except ImportError as e:
    print(f"Error: {e}")

print("Step 3: Importing DataScientist")
try:
    from agents.intelligence_cluster import DataScientist
    print("Success: DataScientist imported")
except ImportError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Exception: {e}")

print("Done")
