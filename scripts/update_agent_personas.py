import os

agents_dir = r"e:\ABHINAV\MR.VERMA\.agent\agents"

agents = [f for f in os.listdir(agents_dir) if f.endswith('.md')]

for agent_file in agents:
    path = os.path.join(agents_dir, agent_file)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. Update frontmatter with optimization skills if missing
    if "skills:" in content:
        if "poweruseage" not in content:
            content = content.replace("skills:", "skills:\n  - poweruseage\n  - memory-optimization\n  - using-superpowers")
    
    # 2. Inject Harmony Protocol section
    if "## 🕸️ Spider Web Harmony" not in content:
        harmony_section = """
## 🕸️ Spider Web Harmony
- **Synchronization**: Proactively cross-reference `@[/workflows]` and `@[agent-skills]`.
- **Optimization**: All outputs MUST follow `@[/poweruseage]` Level 3 (Symbolic Density).
- **Efficiency**: Conduct mandatory memory profiling per `@[/memory-optimization]`.
- **Integrity**: Any task with >1% variance requires `@[/using-superpowers]` activation.
"""
        # Inject before routing trigger if exists, else at end
        if "## 🚦 Routing Trigger" in content:
            content = content.replace("## 🚦 Routing Trigger", harmony_section + "\n## 🚦 Routing Trigger")
        else:
            content += harmony_section
            
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Updated {len(agents)} agent personas.")
