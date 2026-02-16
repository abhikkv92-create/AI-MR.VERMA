import json
import logging
import os

from core.ai.primary_engine import PrimaryAIEngine

logger = logging.getLogger("Kernel.Evolution")

class SelfEvolver:
    """
    Higher-order module that analyzes system state and applies 'evolutionary' upgrades.
    In this Next Gen state, it focuses on hyperparameter tuning and prompt refinement.
    """

    def __init__(self, engine: PrimaryAIEngine):
        self.engine = engine
        self.config_path = os.path.join(os.getcwd(), "core", "evolution_config.json")
        self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "version": "2.0.0",
                "primary_temp": 0.23,
                "vision_concurrency": 5,
                "routing_enabled": True
            }

    def _save_config(self):
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=4)

    async def evolve(self):
        """
        Runs the evolution loop: Analyze -> Decision -> Upgrade.
        """
        logger.info("Executing Self-Evolution Cycle...")

        # 1. Analyze (Simulated by asking Primary Engine to reflect on current config)
        prompt = (
            f"Current System Config: {json.dumps(self.config)}\n"
            "Analyze these parameters for an i9-13900H system with a 27-agent swarm. "
            "Suggest upgrades to maximize intelligence and throughput. "
            "Output JSON with 'upgrades' object."
        )

        try:
            completion = self.engine.generate(
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            strategy = completion.choices[0].message.content

            # Extract JSON from strategy (LLM output might have markdown)
            if "```json" in strategy:
                strategy = strategy.split("```json")[1].split("```")[0].strip()

            upgrades = json.loads(strategy).get("upgrades", {})

            if upgrades:
                logger.info(f"Applying Evolution Upgrades: {upgrades}")
                self.config.update(upgrades)
                self.config["version"] = f"2.1.{int(os.environ.get('EVO_COUNT', 0)) + 1}"
                self._save_config()
                return True

        except Exception as e:
            logger.error(f"Evolution Cycle Failed: {e}")
            return False

        return False

# Integrated Evolution Singleton
async def initiate_evolution(engine):
    evolver = SelfEvolver(engine)
    return await evolver.evolve()
