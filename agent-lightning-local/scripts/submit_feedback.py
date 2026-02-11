"""
Feedback Submission Script
──────────────────────────
Use this to submit user ratings for interactions.
These ratings are the strongest reward signal for training.

USAGE:
  python submit_feedback.py <interaction_id> good
  python submit_feedback.py <interaction_id> bad
  python submit_feedback.py <interaction_id> adopted    (code was used)
  python submit_feedback.py <interaction_id> rejected   (code was not used)
"""

import os
import sys
import glob
import json

INTERACTION_DIR = "/app/data/interactions"


def submit(interaction_id: str, feedback_type: str):
    found = False
    for filepath in glob.glob(os.path.join(INTERACTION_DIR, "interactions_*.jsonl")):
        lines = []
        with open(filepath, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                if data.get("id") == interaction_id:
                    if feedback_type in ("good", "bad"):
                        data["rating"] = feedback_type
                    elif feedback_type == "adopted":
                        data["code_adopted"] = True
                    elif feedback_type == "rejected":
                        data["code_adopted"] = False
                    # Reset reward so it gets recomputed
                    data["reward_score"] = None
                    found = True
                lines.append(json.dumps(data))

        if found:
            with open(filepath, "w") as f:
                f.write("\n".join(lines) + "\n")
            print(f"Feedback recorded: {interaction_id} → {feedback_type}")
            return

    print(f"Interaction {interaction_id} not found.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python submit_feedback.py <interaction_id> <good|bad|adopted|rejected>")
        sys.exit(1)
    submit(sys.argv[1], sys.argv[2])
