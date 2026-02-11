import subprocess
import os
import sys
import shutil

SKILLS_TO_ACQUIRE = [
    "vercel-labs/skills@find-skills",
    "vercel-labs/agent-skills@vercel-react-best-practices",
    "vercel-labs/agent-skills@web-design-guidelines",
    "remotion-dev/skills@remotion-best-practices",
    "browser-use/browser-use@browser-use",
    "vercel-labs/agent-skills@vercel-react-native-skills",
    "nextlevelbuilder/ui-ux-pro-max-skill@ui-ux-pro-max",
    "squirrelscan/skills@audit-website",
    "coreyhaines31/marketingskills@seo-audit",
    "supabase/agent-skills@supabase-postgres-best-practices",
    "obra/superpowers@brainstorming",
    "anthropics/skills@pdf",
    "coreyhaines31/marketingskills@copywriting",
    "anthropics/skills@pptx",
    "better-auth/skills@better-auth-best-practices",
    "anthropics/skills@xlsx",
    "anthropics/skills@docx",
    "expo/skills@building-native-ui",
    "vercel-labs/next-skills@next-best-practices",
    "anthropics/skills@frontend-design",
    "vercel-labs/agent-skills@vercel-composition-patterns",
    "anthropics/skills@skill-creator",
    "vercel-labs/agent-browser@agent-browser",
    "obra/superpowers@systematic-debugging",
    "coreyhaines31/marketingskills@marketing-psychology",
    "obra/superpowers@writing-plans"
]

PLANTSKILLS_DIR = "e:/ABHINAV/MR.VERMA/plantskills/skills"
TEMP_AGENTS_DIR = os.path.join(PLANTSKILLS_DIR, ".agents/skills")

def acquire_skill(skill_name):
    print(f"--- Acquiring {skill_name} ---")
    
    # Extract short name (after @)
    short_name = skill_name.split("@")[-1] if "@" in skill_name else skill_name.split("/")[-1]
    
    # Run npx skills add
    # We send 4 newlines: 
    # 1. Project scope
    # 2. Symlink/Copy method
    # 3. Proceed with installation
    # 4. Install confirm (for some skills)
    command = ["npx", "skills", "add", skill_name, "--agent", "antigravity"]
    
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PLANTSKILLS_DIR,
            shell=True, # Needed for npx on Windows
            encoding='utf-8',
            errors='replace'
        )
        
        # Send inputs
        out, err = process.communicate(input="\n\n\n\n", timeout=60)
        
        if process.returncode != 0:
            print(f"Error acquiring {skill_name}: {err}")
            return False
        
        print(f"Successfully downloaded {skill_name}")
        
        # Move from .agents/skills to plantskills/skills
        src = os.path.join(TEMP_AGENTS_DIR, short_name)
        dst = os.path.join(PLANTSKILLS_DIR, short_name)
        
        if os.path.exists(src):
            if os.path.exists(dst):
                print(f"Updating existing skill: {short_name}")
                shutil.rmtree(dst)
            shutil.move(src, dst)
            print(f"Integrated {short_name} into plantskills")
            return True
        else:
            print(f"Skill directory not found at {src}")
            return False
            
    except Exception as e:
        print(f"Failed to process {skill_name}: {e}")
        return False

def main():
    if not os.path.exists(PLANTSKILLS_DIR):
        print(f"Error: Target directory {PLANTSKILLS_DIR} does not exist.")
        sys.exit(1)
        
    success_count = 0
    for skill in SKILLS_TO_ACQUIRE:
        if acquire_skill(skill):
            success_count += 1
            
    print(f"\n--- Batch Acquisition Complete ---")
    print(f"Success: {success_count}/{len(SKILLS_TO_ACQUIRE)}")

if __name__ == "__main__":
    main()
