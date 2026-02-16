import logging
from typing import Any, Dict

from agents.base_agent import BaseAgent
from core.ai.primary_engine import PrimaryAIEngine

logger = logging.getLogger("Kernel.SwarmNode")

class UnifiedSwarmNode(BaseAgent):
    """
    A Quantum-Lite agent node that can dynamically specialize 
    into any role (Frontend, Backend, Intelligence, etc.) 
    using JIT prompt injection.
    """

    def __init__(self, name: str, cluster: str, engine: PrimaryAIEngine):
        # We initialize with a generic 'Node' role, which will be specialized during execution
        super().__init__(name=name, role="DynamicNode", cluster=cluster)
        self.engine = engine
        self._role_definition = ""

    def specialize(self, role_definition: str):
        """Injects the specialized intelligence into the node."""
        self._role_definition = role_definition
        logger.info(f"Node {self.name} specialized as: {role_definition[:30]}...")

    async def _execute_task_logic(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes logic using the Primary Engine and the injected role definition.
        """
        instruction = task_data.get("instruction", "NO_INSTRUCTION")

        system_prompt = (
            f"You are the {self.name} node of MR.VERMA. "
            f"Your current specialized cluster is: {self.cluster}. "
            f"Role Definition: {self._role_definition}\n\n"
            "Execute the task with extreme efficiency. Use [POWERUSEAGE Level 3]."
        )

        try:
            # Shift to Semantic English protocol for inter-node communication
            completion = self.engine.generate(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": instruction}
                ],
                stream=False
            )

            response_content = completion.choices[0].message.content
            return {
                "status": "COMPLETE",
                "node": self.name,
                "cluster": self.cluster,
                "response": response_content
            }
        except Exception as e:
            logger.error(f"Node {self.name} execution failed: {e}")
            raise
