import os
import sys
import logging

# Add project root to path for core imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from core.plugin_orchestrator import orchestrator as plugin_orchestrator

log = logging.getLogger(__name__)

class SkillsManager:
    """
    Manages the indexing and retrieval of PlantSkills.
    Implements a simple Keyword + Vector (Simulated) RAG.
    """
    def __init__(self, base_dir="/app/plantskills"):
        self.base_dir = base_dir
        self.skills_dir = os.path.join(base_dir, "skills")
        self.agents_dir = os.path.join(base_dir, "agents")
        self.workflows_dir = os.path.join(base_dir, "workflows")

        self.skills_index = {}
        self.agents_index = {}
        self.workflows_index = {}

        self._build_index()

    def _build_index(self):
        """Scan Skills, Agents, and Workflows."""
        if not os.path.exists(self.base_dir):
            log.warning(f"PlantSkills base directory not found: {self.base_dir}")
            return

        # 1. Index Skills
        skill_files = glob.glob(os.path.join(self.skills_dir, "**", "SKILL.md"), recursive=True)
        for filepath in skill_files:
            try:
                folder_name = os.path.basename(os.path.dirname(filepath))
                self.skills_index[folder_name] = {"path": filepath}
            except Exception: pass

        # 2. Index Agents
        agent_files = glob.glob(os.path.join(self.agents_dir, "*.md"))
        for filepath in agent_files:
            try:
                name = os.path.basename(filepath).replace(".md", "")
                self.agents_index[name] = {"path": filepath}
            except Exception: pass

        # 3. Index Workflows
        workflow_files = glob.glob(os.path.join(self.workflows_dir, "*.md"))
        for filepath in workflow_files:
            try:
                name = os.path.basename(filepath).replace(".md", "")
                self.workflows_index[name] = {"path": filepath}
            except Exception: pass

        log.info(f"Indexed: {len(self.skills_index)} Skills, {len(self.agents_index)} Agents, {len(self.workflows_index)} Workflows.")

    def get_content(self, path):
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except: return None

    def get_agent_persona(self, agent_name):
        """Retrieve full agent persona (Checks legacy and Next-Gen plugins)."""
        cleaned_name = agent_name.replace("@", "").lower().strip()
        
        # 1. Check Legacy Index
        if cleaned_name in self.agents_index:
            return self.get_content(self.agents_index[cleaned_name]["path"])
            
        # 2. Check Next-Gen Plugin Orchestrator
        plugin_agent = plugin_orchestrator.get_agent(cleaned_name)
        if plugin_agent:
            log.info(f"Retrieved Next-Gen agent: {cleaned_name}")
            return f"{plugin_agent['content']}"

        return None

    def get_workflow(self, workflow_name):
        """Retrieve full workflow."""
        cleaned_name = workflow_name.replace("/", "").replace("@", "").lower().strip()
        if cleaned_name in self.workflows_index:
            return self.get_content(self.workflows_index[cleaned_name]["path"])
        return None

    def get_skill_content(self, skill_name):
        """Retrieve full content of a skill."""
        if skill_name in self.skills_index:
            return self.get_content(self.skills_index[skill_name]["path"])
        return None

    def find_relevant_skills(self, query):
        """
        Find relevant skills based on query keywords.
        """
        query = query.lower()
        matches = []

        # Priority: Exact match in skill name
        for name in self.skills_index:
            if name in query or query in name:
                matches.append(name)

        # Limit to top 1
        return matches[:1]
