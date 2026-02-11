import json
import time
import os

DATA_DIR = r"e:\ABHINAV\MR.VERMA\agent-lightning-local\data\interactions"
os.makedirs(DATA_DIR, exist_ok=True)

agents = ["frontend-specialist", "backend-specialist", "security-auditor", "orchestrator"]

for i, agent in enumerate(agents):
    interaction_id = f"test-{int(time.time())}-{i}"
    log_entry = {
        "id": interaction_id,
        "timestamp": time.time(),
        "datetime": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "request": {"messages": [{"role": "user", "content": f"Test for @{agent}"}]},
        "response": {"content": f"Acknowledged from {agent}."},
        "model": "local-coder",
        "agent_name": agent,
        "latency": 0.5,
        "feedback": None
    }
    
    filepath = os.path.join(DATA_DIR, f"interactions_{interaction_id}.jsonl")
    with open(filepath, "w") as f:
        f.write(json.dumps(log_entry) + "\n")

print(f"Seeded {len(agents)} test interactions to {DATA_DIR}")
