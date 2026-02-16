import logging
from typing import List

from core.ai.primary_engine import PrimaryAIEngine

logger = logging.getLogger("Kernel.SemanticRouter")

class SemanticRouter:
    """
    Intelligently routes requests to the 27+ specialist agents.
    Uses LLM-based categorization for high-precision delegation.
    """
    def __init__(self, engine: PrimaryAIEngine):
        self.engine = engine
        self.agent_map = {
            "FRONTEND": ["FrontendSpecialist", "UIDesigner", "MobileDeveloper"],
            "BACKEND": ["BackendArchitect", "DatabaseDesigner", "APIDeveloper"],
            "INTELLIGENCE": ["AIMLEngineer", "ResearchAnalyst", "DataScientist"],
            "PLATFORM": ["DevOpsEngineer", "SecurityArchitect", "ProductionOrchestrator"]
        }

    async def route(self, refined_prompt: str) -> List[str]:
        """
        Determines which agent clusters or specific agents should handle the prompt.
        """
        system_prompt = (
            "You are the MR.VERMA V5.0 Semantic Dispatcher. "
            "Determine the target agent clusters based on the natural intent and 'Vibe' of the instruction. "
            "Active Clusters: FRONTEND, BACKEND, INTELLIGENCE, PLATFORM. "
            "Identify ALL clusters that might be relevant for recursive execution. "
            "Respond in a natural, comma-separated list. No JSON."
        )

        try:
            # We use stream=False for internal routing logic to simplify
            completion = self.engine.generate(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": refined_prompt}
                ],
                stream=False
            )

            # OpenAI/NVIDIA API returns ChatCompletion if stream=False
            content = completion.choices[0].message.content.upper()
            activated_clusters = [c.strip() for c in content.split(",") if c.strip() in self.agent_map]

            if not activated_clusters:
                logger.warning("No clusters activated. Defaulting to all clusters for safety.")
                return list(self.agent_map.keys())

            logger.info(f"Route Selected: {activated_clusters}")
            return activated_clusters

        except Exception as e:
            logger.error(f"Routing Failed: {e}")
            return list(self.agent_map.keys()) # Fallback to all agents
