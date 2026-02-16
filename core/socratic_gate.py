
import json
import logging
import os
from typing import Any, Dict

import requests

# Configure logging
logger = logging.getLogger("Kernel.SocraticGate")

class SocraticGate:
    """
    The Socratic Gate acts as the 'Conscience' of the system.
    It intercepts user requests and uses the NVIDIA AI Intelligence to:
    1. Clarify Vague Requests.
    2. Assess Safety/Risk.
    3. Refine Technical Requirements.
    """

    def __init__(self):
        self.api_key = os.environ.get("NVIDIA_API_KEY")
        self.api_url = os.environ.get("NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
        self.model = os.environ.get("NVIDIA_MODEL", "moonshotai/kimi-k2.5")

        if not self.api_key:
            logger.warning("NVIDIA_API_KEY missing. Socratic Gate running in PASS-THROUGH mode.")

    def interrogate(self, user_request: str) -> Dict[str, Any]:
        """
        Analyzes the user request and returns a structured assessment.
        """
        if not self.api_key:
            return {"status": "PASSED", "reason": "No API Key", "refined_prompt": user_request}

        logger.info("Interrogating user request via NVIDIA AI...")

        system_prompt = (
            "You are the Socratic Gatekeeper for the MR.VERMA AI System. "
            "Your job is to analyze the User Request for Clarity, Safety, and Completeness. "
            "NOTE: The system has Vision capabilities. If the user provides an image path or asks to analyze an image, extract the path."
            "Output JSON ONLY: {"
            "  'status': 'PASSED' | 'CLARIFICATION_NEEDED' | 'BLOCKED', "
            "  'reason': 'Explanation', "
            "  'refined_prompt': 'Optimized version of the prompt', "
            "  'risk_score': 0-10, "
            "  'image_path': 'path/to/image.png' (or null)"
            "}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_request}
            ],
            "max_tokens": 1000,
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                # Clean markdown code blocks if present
                if "```json" in content:
                    content = content.replace("```json", "").replace("```", "")

                analysis = json.loads(content)
                logger.info(f"Gate Assessment: {analysis['status']} (Risk: {analysis.get('risk_score')})")
                return analysis
            else:
                logger.error(f"AI Error {response.status_code}: {response.text}")
                return {"status": "PASSED", "reason": "AI Error", "refined_prompt": user_request}

        except Exception as e:
            logger.error(f"Socratic Exception: {e}")
            return {"status": "PASSED", "reason": "Exception", "refined_prompt": user_request}
