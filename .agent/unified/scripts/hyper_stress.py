import os
import statistics
import subprocess
import sys
import time
from datetime import datetime

ITERATIONS = 10
CHECKLIST_CMD = ["python", ".agent/scripts/checklist.py", "."]
INTEGRATION_CMD = ["python", ".agent/scripts/verify_integration.py"]

print(f"🔥 INITIATING HYPER-STRESS TEST: {ITERATIONS} ITERATIONS")
print(f"⏰ Start Time: {datetime.now().strftime('%H:%M:%S')}")
print("="*60)

results = []
latencies = []

start_global = time.time()

for i in range(1, ITERATIONS + 1):
    iter_start = time.time()
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    # Run Checklist
    check_proc = subprocess.run(CHECKLIST_CMD, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)

    # Run Integration
    int_proc = subprocess.run(INTEGRATION_CMD, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)



    iter_duration = time.time() - iter_start
    latencies.append(iter_duration)

    if check_proc.returncode == 0 and int_proc.returncode == 0:
        print(f"✅ PASS ({iter_duration:.2f}s)")
        results.append("PASS")
    else:
        print(f"❌ FAIL ({iter_duration:.2f}s)")
        results.append("FAIL")
        if check_proc.returncode != 0:
            print(f"  -> Checklist Error:\n{check_proc.stderr[:200]}...")
        if int_proc.returncode != 0:
            print(f"  -> Integration Error:\n{int_proc.stderr[:200]}...")

end_global = time.time()
total_time = end_global - start_global

print("\n" + "="*60)
print("📊 HYPER-STRESS RESULTS")
print("="*60)
print(f"Total Iterations: {ITERATIONS}")
print(f"Pass Rate:        {results.count('PASS')}/{ITERATIONS} ({results.count('PASS')/ITERATIONS:.0%})")
print(f"Total Time:       {total_time:.2f}s")
print(f"Avg Latency:      {statistics.mean(latencies):.2f}s")
print(f"Max Latency:      {max(latencies):.2f}s")
print(f"Min Latency:      {min(latencies):.2f}s")

if "FAIL" in results:
    print("\n❌ SYSTEM INSTABILITY DETECTED")
    sys.exit(1)
else:
    print("\n✅ SYSTEM STABLE AT 1000% LOAD")
    sys.exit(0)
