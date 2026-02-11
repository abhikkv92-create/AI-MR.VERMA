import os

workflows_dir = r"e:\ABHINAV\MR.VERMA\.agent\workflows"
workflows = [f for f in os.listdir(workflows_dir) if f.endswith('.md')]

# Mapping common terms to agents/workflows
connections = {
    "frontend": "/frontend-specialist",
    "ui": "/frontend-specialist",
    "ux": "/frontend-specialist",
    "backend": "/backend-specialist",
    "api": "/backend-specialist",
    "database": "/database-architect",
    "security": "/security-auditor",
    "test": "/test-engineer",
    "qa": "/qa-automation-engineer",
    "deploy": "/deploy",
    "performance": "/performance-optimizer",
    "mobile": "/mobile-developer",
    "docs": "/documentation-writer",
    "plan": "/plan",
    "debug": "/debug",
}

for wf_file in workflows:
    path = os.path.join(workflows_dir, wf_file)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "## 🕸️ Spider Web Sync" in content:
        continue
        
    found_links = []
    for key, link in connections.items():
        if key in content.lower() and link not in wf_file.lower():
            if link not in found_links:
                found_links.append(link)
    
    if found_links:
        sync_section = "\n## 🕸️ Spider Web Sync\n"
        sync_section += "- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.\n"
        sync_section += "- **Related Triggers**: " + ", ".join([f"`{link}`" for link in found_links]) + ".\n"
        content += sync_section
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

print(f"Interconnected {len(workflows)} workflows.")
