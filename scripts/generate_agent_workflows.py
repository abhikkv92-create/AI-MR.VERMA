import os

agents_dir = r"e:\ABHINAV\MR.VERMA\.agent\agents"
workflows_dir = r"e:\ABHINAV\MR.VERMA\.agent\workflows"

agents = [f.replace('.md', '') for f in os.listdir(agents_dir) if f.endswith('.md')]

for agent in agents:
    workflow_content = f"""---
description: Activate the {agent.replace('-', ' ').title()} specialist agent
---
# Trigger: /{agent}

Use this command to specifically engage the **{agent}** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific {agent} requirements in the user request.
   - Cross-reference with `@[agent-skills/{agent}]` if applicable.

2. **Engage Agent**
   - Use the **{agent}** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).
"""
    with open(os.path.join(workflows_dir, f"{agent}.md"), "w", encoding="utf-8") as f:
        f.write(workflow_content)

print(f"Generated {len(agents)} agent workflows.")
