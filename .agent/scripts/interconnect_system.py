import os
import re
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(BASE_DIR, "agents")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
WORKFLOWS_DIR = os.path.join(BASE_DIR, "workflows")
OUTPUT_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "ARCHITECTURE.md"))

def scan_directory(directory, item_type="generic"):
    if not os.path.exists(directory):
        return []
    items = []
    
    if item_type == "skill":
        # For skills, we look for directories containing SKILL.md
        for root, dirs, files in os.walk(directory):
            if "SKILL.md" in files:
                # The skill name is the folder name
                skill_name = os.path.basename(root)
                items.append(skill_name)
    elif item_type == "agent":
         # For agents, we look for .md files in the agents dir
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".md"):
                     items.append(os.path.splitext(file)[0])
    elif item_type == "workflow":
        # For workflows, we look for .md files in the workflows dir
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".md"):
                     items.append(os.path.splitext(file)[0])

    return sorted(list(set(items)))

def generate_architecture_md(agents, skills, workflows):
    content = f"""# 🕸️ AI KIT Architecture (The Hive Spider)

> **Central Nervous System of the Antigravity Kit**
> This map connects {len(agents)} Agents, {len(skills)} Skills, and {len(workflows)} Workflows.

## 1. 🤖 Agent Registry (The Brains)
| Agent Name | Role | Primary Skills |
|------------|------|----------------|
"""
    for agent in agents:
        content += f"| `@{agent}` | Specialist | [View Skills](.agent/agents/{agent}.md) |\n"

    content += f"""
## 2. ⚡ Skill Matrix (The Capabilities)
| Skill Name | Description | Workflow Command |
|------------|-------------|------------------|
"""
    for skill in skills:
        workflow_cmd = f"/{skill}" if skill in workflows else "❌ Missing"
        content += f"| `@{skill}` | Capability | `{workflow_cmd}` |\n"

    content += f"""
## 3. 🔄 Workflow Directory (The Actions)
| Workflow | Trigger | Linked Skill |
|----------|---------|--------------|
"""
    for workflow in workflows:
        linked_skill = f"@{workflow}" if workflow in skills else "Custom Flow"
        content += f"| `/{workflow}` | Slash Command | `{linked_skill}` |\n"

    content += """
## 4. 🔗 Connectivity Graph (Mermaid)
```mermaid
graph TD
    subgraph Agents
"""
    for i, agent in enumerate(agents[:5]): # Limit for readability
        content += f"        A{i}[{agent}]\n"
    
    content += """    end
    subgraph Workflows
"""
    for i, wf in enumerate(workflows[:5]):
        content += f"        W{i}[/{wf}]\n"

    content += """    end
    
    %% Connections (Example)
    A0 --> W0
    A1 --> W1
```
"""
    return content

def main():
    print(f"Scanning Agents in {AGENTS_DIR}")
    agents = scan_directory(AGENTS_DIR, "agent")
    
    print(f"Scanning Skills in {SKILLS_DIR}")
    skills = scan_directory(SKILLS_DIR, "skill")
    
    print(f"Scanning Workflows in {WORKFLOWS_DIR}")
    workflows = scan_directory(WORKFLOWS_DIR, "workflow")

    print(f"Found: {len(agents)} Agents, {len(skills)} Skills, {len(workflows)} Workflows")
    
    arch_content = generate_architecture_md(agents, skills, workflows)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(arch_content)
        
    print(f"Successfully created {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
