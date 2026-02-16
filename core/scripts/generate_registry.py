import os
import re

AGENTS_DIR = r"e:\ABHINAV\MR.VERMA\plugins\agents"
OUTPUT_FILE = r"e:\ABHINAV\MR.VERMA\documentation\AGENTS.md"

def parse_agent(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Extract name and description from frontmatter
    name_match = re.search(r"name:\s*(.+)", content)
    desc_match = re.search(r"description:\s*(.+)", content)

    name = name_match.group(1).strip() if name_match else os.path.basename(filepath).replace(".md", "")
    desc = desc_match.group(1).strip().strip('"').strip("'") if desc_match else "No description provided."

    return name, desc

def generate_registry():
    if not os.path.exists(AGENTS_DIR):
        print("Agents directory not found.")
        return

    agents = []
    for filename in os.listdir(AGENTS_DIR):
        if filename.endswith(".md"):
            try:
                name, desc = parse_agent(os.path.join(AGENTS_DIR, filename))
                agents.append((name, desc))
            except Exception as e:
                print(f"Skipping {filename}: {e}")

    agents.sort()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# 🤖 MR.VERMA 3.0: Agent Swarm Registry\n\n")
        f.write(f"**Total Active Agents:** {len(agents)}\n\n")
        f.write("| Agent Name | Description |\n")
        f.write("|------------|-------------|\n")
        for name, desc in agents:
            # Escape pipes to prevent table breakage
            desc = desc.replace("|", "\\|")
            # Truncate desc if too long for table
            short_desc = (desc[:100] + "...") if len(desc) > 100 else desc
            f.write(f"| `@{name}` | {short_desc} |\n")

    print(f"Successfully generated AGENTS.md with {len(agents)} agents.")

if __name__ == "__main__":
    generate_registry()
