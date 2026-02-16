import logging
import os
import re
from typing import Any, Dict, List, Optional

import yaml


class PluginOrchestrator:
    """
    Unified loader for Agents, Skills, and Hooks following the aitmpl.com/Claude Code format.
    Enables dynamic, hot-reloadable system extensions.
    """

    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
        self.registry = {
            "agents": {},
            "commands": {},
            "hooks": {}
        }
        self.logger = logging.getLogger("MR.VERMA.PluginOrchestrator")

    def initialize(self):
        """Initial scan and registration of plugins."""
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
            for sub in ["agents", "commands", "hooks"]:
                os.makedirs(os.path.join(self.plugins_dir, sub))

        self.reload_all()

    def reload_all(self):
        """Reloads all components from the plugins directory."""
        self.logger.info("Reloading all plugins...")
        self.registry["agents"] = self._scan_directory("agents")
        self.registry["commands"] = self._scan_directory("commands")
        self.registry["hooks"] = self._scan_directory("hooks")
        self.logger.info(f"Registry updated: {len(self.registry['agents'])} agents, "
                         f"{len(self.registry['commands'])} commands, "
                         f"{len(self.registry['hooks'])} hooks.")

    def _scan_directory(self, category: str) -> Dict[str, Any]:
        """Scans a category subdirectory for Markdown components."""
        components = {}
        target_dir = os.path.join(self.plugins_dir, category)

        if not os.path.exists(target_dir):
            return components

        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".md"):
                    path = os.path.join(root, file)
                    component = self._parse_component(path)
                if component:
                    metadata = component.get("metadata")
                    if isinstance(metadata, dict):
                        name = metadata.get("name", file.replace(".md", ""))
                        components[name] = component
                    else:
                        self.logger.warning(f"Skipping {file}: Metadata is not a dictionary.")
        return components

    def _parse_component(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parses a Markdown file with YAML frontmatter."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Regex to extract YAML frontmatter (between --- and ---)
            match = re.search(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL | re.MULTILINE)
            if match:
                yaml_content = match.group(1)
                body_content = match.group(2)
                metadata = yaml.safe_load(yaml_content)

                # Normalize 'tools' to list if it's a string
                if "tools" in metadata and isinstance(metadata["tools"], str):
                    metadata["tools"] = [t.strip() for t in metadata["tools"].split(",") if t.strip()]

                return {
                    "metadata": metadata,
                    "content": body_content.strip(),
                    "path": file_path
                }
            else:
                self.logger.warning(f"Component at {file_path} missing frontmatter.")
                return None
        except Exception as e:
            self.logger.error(f"Failed to parse component at {file_path}: {e}")
            return None

    def get_agent(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieves an agent by name."""
        return self.registry["agents"].get(name)

    def list_agents(self) -> List[str]:
        """Lists all registered agents."""
        return list(self.registry["agents"].keys())

    def get_command(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieves a command by name."""
        return self.registry["commands"].get(name)

    def get_hook(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieves a hook by name."""
        return self.registry["hooks"].get(name)

# Singleton instance for system-wide access
orchestrator = PluginOrchestrator()
