import ast
import logging
import os
from typing import Dict, List, Set

from core.memory_service import memory_service

logger = logging.getLogger("Kernel.Discovery")

class DependencyGraph:
    """
    Auto-Discovery Graph: Maps codebase relationships into the Neural Brain (Milvus).
    Enables the Orchestrator to understand 'impact zones' before making changes.
    """

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.graph: Dict[str, Set[str]] = {}

    def scan(self):
        """Recursively scans the codebase to build a dependency map."""
        logger.info(f"Initiating Codebase Scan in: {self.root_dir}")
        for root, _, files in os.walk(self.root_dir):
            if ".git" in root or "__pycache__" in root or ".gemini" in root:
                continue

            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.root_dir)
                    self.graph[rel_path] = self._get_imports(full_path)

    def _get_imports(self, file_path: str) -> Set[str]:
        """Parses a Python file to extract import statements."""
        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())

            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
            return imports
        except Exception as e:
            logger.debug(f"Failed to parse {file_path}: {e}")
            return set()

    async def sync_to_brain(self):
        """Stores the dependency graph in the Neural Brain for RAG-based context."""
        logger.info("Synchronizing Dependency Graph with Neural Recall...")
        for file, deps in self.graph.items():
            if not deps: continue

            content = f"File '{file}' depends on: {', '.join(deps)}"
            metadata = {
                "type": "dependency_mapping",
                "source": file,
                "dependencies": list(deps)
            }
            await memory_service.store(content, metadata)
        logger.info("Dependency Graph Synchronization Complete.")

    def get_impact_zone(self, file_path: str) -> List[str]:
        """Identifies which files depend on the specified file."""
        impacted = []
        for file, deps in self.graph.items():
            # Check for direct or partial name matches (simplification)
            base_name = os.path.basename(file_path).replace(".py", "")
            if any(base_name in d for d in deps):
                impacted.append(file)
        return impacted
