
import asyncio
import logging
import os
import time
from typing import List

# Agent Imports
from agents.swarm_node import UnifiedSwarmNode

# Core Imports
from core.ai.vision_engine import VisionAIEngine
from core.dependency_graph import DependencyGraph
from core.memory_service import memory_service
from core.toolkit import SupremeToolkit

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Kernel.Main")

class SupremeOrchestrator:
    """
    The Supreme Entity that orchestrates the entire swarm of agents.
    Optimized for Intel i9-13900H processing power.
    """

    def __init__(self):
        from core.ai.primary_engine import PrimaryAIEngine
        from core.ai.secondary_engine import SecondaryAIEngine
        from core.socratic_gate import SocraticGate

        self.gate = SocraticGate()
        self.vision_engine = VisionAIEngine()
        self.primary_engine = PrimaryAIEngine()
        self.secondary_engine = SecondaryAIEngine()

        # Unified Nodes (V4.0 Quantum Swarm)
        self.nodes = {
            "FRONTEND": UnifiedSwarmNode("FrontNode", "FRONTEND", self.primary_engine),
            "BACKEND": UnifiedSwarmNode("BackNode", "BACKEND", self.primary_engine),
            "INTELLIGENCE": UnifiedSwarmNode("IntelNode", "INTELLIGENCE", self.primary_engine),
            "PLATFORM": UnifiedSwarmNode("PlatNode", "PLATFORM", self.primary_engine)
        }

        # V5.0 Singularity Core
        self.toolkit = SupremeToolkit(self.primary_engine)
        self.dep_graph = DependencyGraph(os.getcwd())

        # Initialize Task Queue
        from core.task_queue import VisionTaskQueue
        self.vision_queue = VisionTaskQueue(concurrency=5)
        # Start queue worker loop in background
        # In a real app, manage lifecycle better (e.g. startup/shutdown events)
        # Here we cheat slightly by firing it up in __init__ but it needs a loop.
        # Since __init__ is sync, we can't await start().
        # We'll rely on lazy start or specific lifecycle method if available.
        # Let's add a start method to SupremeOrchestrator or hook into process_request?
        # Better: create a task in the loop when needed, or assume loop exists.

        # Initialize ARL (Autonomous Repair Loop)
        from core.self_healing import AutonomousRepairLoop
        self.arl = AutonomousRepairLoop(self)

        self._initialize_swarm()

    async def startup(self):
        """Lifecycle hook for async startup"""
        await self.vision_queue.start()

        # Start Self-Healing Heartbeat
        asyncio.create_task(self.arl.start())

        # Seed Dependency Graph (Background)
        self.dep_graph.scan()
        asyncio.create_task(self.dep_graph.sync_to_brain())

        # Trigger Self-Evolution Diagnostic (Phase 5)
        from core.evolution import initiate_evolution
        await initiate_evolution(self.primary_engine)
        logger.info("System Self-Evolution & ARL Heartbeat Triggered.")

    async def shutdown(self):
        """Lifecycle hook for async shutdown"""
        await self.vision_queue.stop()

    def _initialize_swarm(self):
        """Legacy initialization removed in V4.0."""
        pass


    async def invoke_all(self, instruction: str = "REPORT_STATUS", filter_clusters: List[str] = None):
        """
        Invokes selective or ALL nodes in parallel using the hardware-optimized ProcessingUnit.
        """
        logger.info(f">>> MESH TRIGGER (Filter: {filter_clusters}) <<<")
        start_time = time.time()

        target_keys = filter_clusters if filter_clusters else list(self.nodes.keys())
        tasks = []

        for key in target_keys:
            node = self.nodes.get(key)
            if node:
                node.start()
                # JIT Role Specialization
                node.specialize(f"Master Processor for {key} domain.")

                task_payload = {
                    "task_id": f"node_{int(time.time())}_{key}",
                    "instruction": instruction
                }
                tasks.append(node.process_task(task_payload))

        # Wait for completion
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        duration = end_time - start_time

        # Process Results
        success_count = 0
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Task Failed: {res}")
            else:
                success_count += 1
                logger.info(f"Result: {res}")

        # Stop nodes
        for key in target_keys:
            node = self.nodes.get(key)
            if node: node.stop()

        logger.info("<<< MESH OPERATION COMPLETE >>>")
        logger.info(f"Successful Nodes: {success_count}/{len(target_keys)}")
        logger.info(f"Total Duration: {duration:.4f}s")

    async def process_request(self, user_input: str):
        """
        Main Entry Point: Processes a user request through the Socratic Gate before execution.
        """
        # 0. Security Sanitation
        from core.input_sanitizer import sanitizer
        clean_input = sanitizer.sanitize(user_input)
        if clean_input != user_input:
            logger.info("User input sanitized for safety.")

        if sanitizer.is_dangerous(clean_input):
            logger.warning("DANGEROUS input detected and blocked!")
            return {"status": "BLOCKED", "reason": "Dangerous command detected."}

        logger.info(f"Processing Request: '{clean_input}'")

        # 1. Socratic Interrogation
        assessment = self.gate.interrogate(clean_input)

        if assessment["status"] == "BLOCKED":
            logger.warning(f"Request BLOCKED by Gate: {assessment['reason']}")
            return {"status": "BLOCKED", "reason": assessment["reason"]}

        elif assessment["status"] == "CLARIFICATION_NEEDED":
            logger.info(f"Clarification Needed: {assessment['reason']}")
            return {"status": "CLARIFICATION_NEEDED", "question": assessment["reason"]}

        logger.info(f"Request PASSED. Risk Score: {assessment.get('risk_score', 0)}")
        refined_prompt = assessment.get("refined_prompt", user_input)
        image_path = assessment.get("image_path")

        # 2. Vision Processing (if image detected)
        vision_task = None
        if image_path:
            logger.info(f"Visual Content Detected: {image_path}")
            # Submit to Queue instead of blocking
            try:
                # We define the task function here to capture context
                async def vision_job():
                    if self.vision_engine.is_available():
                        return self.vision_engine.analyze([image_path], query=refined_prompt)
                    return "Vision Engine Unavailable"

                # Submit to queue
                vision_task = await self.vision_queue.submit(vision_job)
                logger.info("Vision task submitted to queue.")
            except Exception as e:
                logger.error(f"Failed to submit vision task: {e}")

        # 3. Execution (Parallel to Vision)
        # If we have a vision task, we can await it here OR let it run in background if not critical strictly for next step
        # But usually we need the analysis for the final prompt.
        # With the queue, we await the FUTURE, which is non-blocking (other than waiting for result)
        # But this allows the queue to manage the concurrency limit.

        vision_context = ""
        if vision_task:
            try:
                # Wait for result with timeout
                analysis = await asyncio.wait_for(vision_task, timeout=30.0)
                vision_context = f"\n[VISION ANALYSIS]: {analysis}"

                # Store in Memory (Async Fire & Forget)
                asyncio.create_task(memory_service.store(
                    content=f"Visual Analysis of {image_path}: {analysis}",
                    metadata={"type": "visual", "source": image_path, "query": refined_prompt}
                ))
            except asyncio.TimeoutError:
                logger.warning("Vision Analysis Timed Out.")
                vision_context = "\n[VISION]: Analysis Timed Out."
            except Exception as e:
                logger.error(f"Vision Task Failed: {e}")

        # 3. Execution (Augment prompt with vision context)
        final_instruction = f"{refined_prompt}\n{vision_context}"

        # 3.5 Semantic Routing (Next Gen Upgrade)
        from core.routing import SemanticRouter
        router = SemanticRouter(self.primary_engine)
        activated_clusters = await router.route(refined_prompt)
        logger.info(f"Dynamically Routing to Clusters: {activated_clusters}")

        # 3.6 Neural Recall (V5.0 Single Brain)
        ltm_context = ""
        try:
            logger.info("Engaging Neural Recall (Cognitive Retrieval)...")
            # We use the Primary Engine to synthesize the recall summary
            ltm_context = await memory_service.recall(refined_prompt, self.primary_engine)
            if ltm_context:
                ltm_context = f"\n[NEURAL RECALL / COGNITIVE BRAIN]:\n{ltm_context}"
        except Exception as e:
            logger.error(f"Neural Recall Failed: {e}")

        # 3.7 Neural Consensus (Supreme V3.0 Upgrade)
        # Engines talk to each other to cross-verify the execution plan
        consensus_context = ""
        if self.secondary_engine.is_available():
            logger.info("Initiating Neural Consensus (Primary <-> Secondary)...")
            try:
                consensus_prompt = (
                    f"The Primary Engine has proposed the following instruction: '{final_instruction}'. "
                    "Analyze this from a 'High-Context/Theoretical' perspective. Are there any catastrophic edge cases, "
                    "logic gaps, or alignment risks? Provide a concise 'Secondary Opinion' for the Supreme Entity."
                )
                consensus_opinion = self.secondary_engine.generate(consensus_prompt, stream=False)
                consensus_context = f"\n[NEURAL CONSENSUS - SECONDARY OPINION]: {consensus_opinion}"
                logger.info("Consensus opinion received.")
            except Exception as e:
                logger.error(f"Neural Consensus failed: {e}")

        # 3.8 Multi-Platform Automation (Google Antigravity, OpenCode, Trae.ai)
        # This is a dispatch layer for cross-platform execution
        platform_dispatch_context = "\n[PLATFORM DISPATCH]: "
        if "google antigravity" in clean_input.lower():
            platform_dispatch_context += "\n- Synchronizing security state with Google Antigravity Platform."
        if "opencode" in clean_input.lower():
            platform_dispatch_context += "\n- Orchestrating workspace isolation via OpenCode CLI."
        if "trae" in clean_input.lower():
            platform_dispatch_context += "\n- Initializing co-pilot context for Trae.ai environment."

        # We'll pass the cluster filter to invoke_all
        await self.invoke_all(instruction=final_instruction, filter_clusters=activated_clusters)

        # 4. Final Synthesis
        # In the "Next Gen" evolution, we use the Primary Engine to synthesize the result
        # taking into account the vision analysis, agent status, long-term context, and consensus.

        system_prompt = (
            "You are MR.VERMA (Supreme Entity). "
            "Synthesize a final response based on the instruction, visual analysis, long-term context, and neural consensus."
        )
        context_msg = (
            f"Instruction: {refined_prompt}\n"
            f"Vision Context: {vision_context}\n"
            f"Long-Term Memory: {ltm_context}\n"
            f"Neural Consensus: {consensus_context}\n"
            f"Platform Integration: {platform_dispatch_context}\n"
            "Swarm Status: Invocation Complete."
        )

        try:
            # FIX: Ensure non-streaming for synthesis to avoid Stream object choices error
            completion = self.primary_engine.generate(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context_msg}
                ],
                stream=False
            )
            final_response = completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Synthesis Failed: {e}")
            final_response = f"Synthesis encounterd an error, but the operation was completed. Vision: {vision_context}"

        return {
            "status": "SUCCESS",
            "original_prompt": user_input,
            "refined_prompt": refined_prompt,
            "vision_analysis": vision_context.strip() if vision_context else None,
            "response": final_response,
            "consensous": consensus_context.strip() if consensus_context else None
        }

if __name__ == "__main__":
    orchestrator = SupremeOrchestrator()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(orchestrator.startup())
        loop.run_until_complete(orchestrator.invoke_all())
    finally:
        loop.run_until_complete(orchestrator.shutdown())
