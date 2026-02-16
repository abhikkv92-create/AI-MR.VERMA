import os
import sys

# Ensure we can import from core
sys.path.append(r"e:\ABHINAV\MR.VERMA")

from core.plugin_orchestrator import PluginOrchestrator


def verify():
    print("Initializing PluginOrchestrator...")
    orchestrator = PluginOrchestrator()
    orchestrator.initialize()

    agents = orchestrator.list_agents()
    print(f"✅ Loaded {len(agents)} agents.")
    print("Agents:")
    for agent in sorted(agents):
        print(f" - {agent}")

    commands = orchestrator.registry["commands"]
    print(f"\n✅ Loaded {len(commands)} commands.")

    hooks = orchestrator.registry["hooks"]
    print(f"\n✅ Loaded {len(hooks)} hooks.")

    skills_dir = r"e:\ABHINAV\MR.VERMA\plantskills\skills"
    if os.path.exists(skills_dir):
        skills = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]
        print(f"\n✅ Verified {len(skills)} skills in plantskills.")
        for skill in sorted(skills):
            print(f" - {skill}")

if __name__ == "__main__":
    verify()
