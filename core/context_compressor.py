import logging
import os
from typing import Dict, List

import requests


class ContextCompressor:
    """
    AI-driven context optimizer for MR.VERMA 3.0.
    Reduces token footprint while preserving critical architectural decisions.
    """

    def __init__(self):
        self.api_key = os.environ.get("NVIDIA_API_KEY")
        self.api_url = os.environ.get("NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
        self.model = os.environ.get("NVIDIA_MODEL", "moonshotai/kimi-k2.5")
        self.logger = logging.getLogger("MR.VERMA.ContextCompressor")

    def compress_history(self, messages: List[Dict[str, str]], target_tokens: int = 4000) -> List[Dict[str, str]]:
        """
        Summarizes older parts of the conversation to fit within token limits.
        """
        if not self.api_key or len(messages) < 10:
            return messages

        self.logger.info(f"Initiating context compression for {len(messages)} messages.")

        # Split: Keep the last 3-4 messages as-is, summarize the rest
        preserved = messages[-4:]
        to_summarize = messages[:-4]

        summary_prompt = (
            "You are the MR.VERMA Context Compressor. Your goal is to summarize the following conversation history. "
            "Focus on: Technical decisions made, File paths mentioned, Current task status, and System constraints. "
            "Remove: Small talk, redundant logs, and repeated greetings. "
            "Output the summary as a SINGLE concise 'system' message."
        )

        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in to_summarize])

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": summary_prompt},
                {"role": "user", "content": history_text}
            ],
            "temperature": 0.2
        }

        try:
            response = requests.post(self.api_url,
                                     headers={"Authorization": f"Bearer {self.api_key}"},
                                     json=payload,
                                     timeout=30)
            if response.status_code == 200:
                summary_content = response.json()["choices"][0]["message"]["content"]
                compressed_history = [
                    {"role": "system", "content": f"PREVIOUS CONTEXT SUMMARY: {summary_content}"}
                ] + preserved
                self.logger.info("Context compression successful.")
                return compressed_history
            else:
                self.logger.warning(f"Compression failed with status {response.status_code}. Using raw history.")
                return messages
        except Exception as e:
            self.logger.error(f"Compression error: {e}")
            return messages

# Singleton instance
compressor = ContextCompressor()
