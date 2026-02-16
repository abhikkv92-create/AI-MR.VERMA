import logging
import os
import shutil

# Configuration
SOURCE_BASE = r"e:\ABHINAV\MR.VERMA\temp_templates\cli-tool\components"
DEST_AGENTS = r"e:\ABHINAV\MR.VERMA\plugins\agents"
DEST_COMMANDS = r"e:\ABHINAV\MR.VERMA\plugins\commands"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def sync_agents():
    source_agents_dir = os.path.join(SOURCE_BASE, "agents")
    if not os.path.exists(source_agents_dir):
        logger.error(f"Source agents dir not found: {source_agents_dir}")
        return

    # Get installed agents (filenames)
    installed_agents = set(f for f in os.listdir(DEST_AGENTS) if f.endswith(".md"))

    # Walk source and find missing
    count = 0
    for root, dirs, files in os.walk(source_agents_dir):
        for file in files:
            if file.endswith(".md"):
                if file not in installed_agents:
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(DEST_AGENTS, file)
                    try:
                        shutil.copy2(src_path, dst_path)
                        logger.info(f"Restored missing agent: {file}")
                        count += 1
                    except Exception as e:
                        logger.error(f"Failed to copy {file}: {e}")
                else:
                    pass # Already exists

    logger.info(f"Agent Sync Complete. Restored {count} agents.")

def sync_commands():
    source_commands_dir = os.path.join(SOURCE_BASE, "commands") # Guessing path
    # If not there, maybe check root docs?
    # Let's try to find them generally if strict path fails

    if not os.path.exists(source_commands_dir):
        # Try to find commands folder
        for root, dirs, files in os.walk(SOURCE_BASE):
            if "commands" in dirs:
                source_commands_dir = os.path.join(root, "commands")
                break

    if source_commands_dir and os.path.exists(source_commands_dir):
         # Similar logic for commands
         os.makedirs(DEST_COMMANDS, exist_ok=True)
         installed_commands = set(f for f in os.listdir(DEST_COMMANDS) if f.endswith(".md"))

         count = 0
         for root, dirs, files in os.walk(source_commands_dir):
            for file in files:
                if file.endswith(".md"):
                     if file not in installed_commands:
                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(DEST_COMMANDS, file)
                        try:
                            shutil.copy2(src_path, dst_path)
                            logger.info(f"Restored missing command: {file}")
                            count += 1
                        except Exception as e:
                            logger.error(f"Failed to copy {file}: {e}")
         logger.info(f"Command Sync Complete. Restored {count} commands.")

if __name__ == "__main__":
    print("Starting Component Sync...")
    sync_agents()
    sync_commands()
    print("Sync Finished.")
