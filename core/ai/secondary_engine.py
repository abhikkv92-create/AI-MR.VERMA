import json
import logging
import os
from collections.abc import Generator
from typing import Any

import requests

# Configure Logging
logger = logging.getLogger("AI.SecondaryEngine")


class SecondaryAIEngine:
    """
    Dedicated engine for high-context, low-speed tasks using Moonshot AI (Kimi-k2.5).
    """

    def __init__(self):
        self.api_key = os.environ.get("NVIDIA_API_KEY_SECONDARY")
        self.api_url = os.environ.get(
            "NVIDIA_API_URL_SECONDARY",
            "https://integrate.api.nvidia.com/v1/chat/completions",
        )
        self.model = "moonshotai/kimi-k2.5"

        if not self.api_key:
            logger.warning(
                "NVIDIA_API_KEY_SECONDARY not set. Secondary engine disabled."
            )

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        stream: bool = True,
        max_tokens: int = 4096,
    ) -> Any:
        if not self.is_available():
            raise ValueError("Secondary Engine is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream" if stream else "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.15,  # Balanced Context for Neural Recall
            "stream": stream,
            "chat_template_kwargs": {"thinking": False},
        }

        try:
            # Significant timeout increase for deep research tasks
            response = requests.post(
                self.api_url, headers=headers, json=payload, stream=stream, timeout=400
            )

            if response.status_code != 200:
                logger.error(f"Engine Error {response.status_code}: {response.text}")
                return None

            if stream:
                return self._stream_generator(response)
            else:
                return response.json()["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None

    def _stream_generator(self, response) -> Generator[str, None, None]:
        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                if decoded.startswith("data: ") and decoded.strip() != "data: [DONE]":
                    try:
                        chunk = json.loads(decoded[6:])
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except:
                        pass
