import os
import re

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
WORKFLOWS_DIR = os.path.join(BASE_DIR, "workflows")

def get_skill_description(skill_path):
    """
    Extracts the description from the SKILL.md frontmatter or first paragraph.
    """
    skill_file = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_file):
        return "No description available."

    try:
        with open(skill_file, encoding="utf-8") as f:
            content = f.read()

        # Try to find YAML frontmatter description
        match = re.search(r"^---\s+.*description:\s*(.*?)\s+---", content, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Fallback: Use the first non-header line
        lines = content.split("\n")
        for line in lines:
            if line.strip() and not line.startswith("#") and not line.startswith("---"):
                return line.strip()[:200] + "..." # Truncate if too long

        return "No description available."
    except Exception as e:
        print(f"Error reading {skill_file}: {e}")
        return "No description available."

def generate_workflow(skill_name, description):
    """
    Generates the markdown content for the workflow.
    """
    # Clean description for YAML (escape quotes if needed, single line)
    clean_desc = description.replace('"', '\\"').replace("\n", " ")

    content = f"""---
description: {clean_desc}
---

# {skill_name} Workflow

1. **Analyze Request**
   - Understand the user's specific need regarding **{skill_name}**.
   - Identify if the task involves {skill_name} best practices, specific patterns, or tool usage.

2. **Activate Skill**
   - Use the `view_file` tool to read the full instructions in:
     `{os.path.join(SKILLS_DIR, skill_name, 'SKILL.md')}`
   - **CRITICAL**: Read the `SKILL.md` file BEFORE proceeding. Do not assume you know the rules.

3. **Execute Strategy**
   - apply the principles and protocols defined in the skill.
   - If the skill provides specific tools or scripts, execute them as needed.

4. **Verify & refine**
   - Ensure the output aligns with the standards set in the skill documentation.
"""
    return content

def main():
    print(f"Scanning skills in: {SKILLS_DIR}")
    print(f"Target workflows dir: {WORKFLOWS_DIR}")

    if not os.path.exists(SKILLS_DIR):
        print("Skills directory not found!")
        return

    if not os.path.exists(WORKFLOWS_DIR):
        os.makedirs(WORKFLOWS_DIR)

    skills = []
    # Recursive scan to match interconnect_system.py logic
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            skills.append(os.path.basename(root))

    print(f"Found {len(skills)} skills (recursive).")

    created_count = 0
    skipped_count = 0

    for skill in skills:
        workflow_filename = f"{skill}.md"
        workflow_path = os.path.join(WORKFLOWS_DIR, workflow_filename)

        # Check if workflow already exists
        if os.path.exists(workflow_path):
            skipped_count += 1
            continue

        # For nested skills, the path to SKILL.md needs to be found correctly.
        # Since 'skill' is just the basename, we need to find the full path again or store it.
        # efficiency fix: Let's store tuples (name, full_path) in the list above.
        pass # Logic handled below in refactored loop

    # REFACTOR: Re-doing the loop to handle paths correctly
    # Recursive scan to match interconnect_system.py logic
    skill_list = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            skill_list.append((os.path.basename(root), root))

    skills = [s[0] for s in skill_list]
    print(f"Found {len(skills)} skills (recursive).")

    for skill_name, skill_path in skill_list:
        workflow_filename = f"{skill_name}.md"
        workflow_path = os.path.join(WORKFLOWS_DIR, workflow_filename)

        if os.path.exists(workflow_path):
            skipped_count += 1
            continue

        description = get_skill_description(skill_path)
        content = generate_workflow(skill_name, description)

        try:
            with open(workflow_path, "w", encoding="utf-8") as f:
                f.write(content)
            created_count += 1
        except Exception as e:
            print(f"Failed to write workflow for {skill_name}: {e}")

    print("-" * 30)
    print("Execution Complete.")
    print(f"Total Skills Processed: {len(skills)}")
    print(f"Workflows Created: {created_count}")
    print(f"Workflows Skipped (Already Existed): {skipped_count}")

if __name__ == "__main__":
    main()
