import logging
import os
import shutil

# Configuration
SOURCE_BASE = r"e:\ABHINAV\MR.VERMA\.claude"
DEST_PLUGINS = r"e:\ABHINAV\MR.VERMA\plugins"
DEST_SKILLS = r"e:\ABHINAV\MR.VERMA\plantskills\skills"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def migrate_agents():
    source = os.path.join(SOURCE_BASE, "agents")
    dest = os.path.join(DEST_PLUGINS, "agents")

    if not os.path.exists(source):
        logger.warning(f"Source agents directory not found: {source}")
        return

    os.makedirs(dest, exist_ok=True)

    for filename in os.listdir(source):
        if filename.endswith(".md"):
            src_file = os.path.join(source, filename)
            dst_file = os.path.join(dest, filename)
            try:
                shutil.copy2(src_file, dst_file)
                logger.info(f"Migrated agent: {filename}")
            except Exception as e:
                logger.error(f"Failed to migrate agent {filename}: {e}")

def migrate_skills():
    # Skills in .claude might be in a 'skills' subdirectory or structured differently depending on the template tool
    # Let's assume standard structure: .claude/skills/<skill_name>/
    source = os.path.join(SOURCE_BASE, "skills")

    if not os.path.exists(source):
         # Sometimes they might be installed directly if using a different structure, but usually .claude/skills
         logger.warning(f"Source skills directory not found at {source}, checking root...")
         # Fallback logic if needed
         return

    os.makedirs(DEST_SKILLS, exist_ok=True)

    for item in os.listdir(source):
        src_path = os.path.join(source, item)
        if os.path.isdir(src_path):
            dst_path = os.path.join(DEST_SKILLS, item)
            if os.path.exists(dst_path):
                logger.info(f"Skill {item} already exists, merging/overwriting...")
                # Remove existing to ensure clean slate or use copytree with dirs_exist_ok=True (Python 3.8+)
                shutil.rmtree(dst_path)

            try:
                shutil.copytree(src_path, dst_path)
                logger.info(f"Migrated skill: {item}")
            except Exception as e:
                logger.error(f"Failed to migrate skill {item}: {e}")

def migrate_commands():
    # Commands typically go to plugins/commands or workflows
    source = os.path.join(SOURCE_BASE, "commands")
    dest_workflows = os.path.join(DEST_PLUGINS, "workflows") # Mapping commands to workflows for now if they are mds

    if not os.path.exists(source):
        logger.warning(f"Source commands directory not found: {source}")
        return

    os.makedirs(dest_workflows, exist_ok=True)

    for filename in os.listdir(source):
        src_file = os.path.join(source, filename)
        # If it's a script, maybe it belongs in scripts? But for VERMA 3.0, we treat them as plugins/commands or workflows
        # If it is .md, likely a workflow. If .py/.js, it's a script.
        # Let's put them in plugins/commands for now
        dest = os.path.join(DEST_PLUGINS, "commands")
        os.makedirs(dest, exist_ok=True)
        dst_file = os.path.join(dest, filename)

        try:
            shutil.copy2(src_file, dst_file)
            logger.info(f"Migrated command: {filename}")
        except Exception as e:
            logger.error(f"Failed to migrate command {filename}: {e}")

if __name__ == "__main__":
    logger.info("Starting Supreme Integration Migration...")
    migrate_agents()
    migrate_skills()
    migrate_commands()
    logger.info("Migration Complete.")
