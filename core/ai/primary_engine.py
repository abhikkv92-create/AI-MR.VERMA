import logging
import os

from openai import OpenAI

# Configure Logging
logger = logging.getLogger("AI.PrimaryEngine")

class PrimaryAIEngine:
    """
    Primary Intelligence Engine (Speed/Logic).
    Now powered by z-ai/glm5 via NVIDIA API.
    """
    def __init__(self):
        self.api_key = os.environ.get("NVIDIA_API_KEY")
        self.base_url = os.environ.get("NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1")
        self.model = os.environ.get("NVIDIA_MODEL", "z-ai/glm5")

        if not self.api_key:
            logger.error("Missing NVIDIA_API_KEY for Primary Engine.")
            raise ValueError("API Key Required")

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def generate(self, messages, tools=None, stream=True, temperature=0.05, top_p=0.1):
        """
        Generates a response using the GLM-5 model.
        Supports streaming and tool calling.
        """
        try:
            extra_body = {"chat_template_kwargs": {"enable_thinking": True, "clear_thinking": False}}

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=16000,
                extra_body=extra_body,
                stream=stream,
                tools=tools,
                tool_choice="auto" if tools else None
            )

            return completion

        except Exception as e:
            logger.error(f"Primary Engine Error: {e}")
            raise

if __name__ == "__main__":
    # Self-test if run directly
    engine = PrimaryAIEngine()
    res = engine.generate([{"role": "user", "content": "Hello GLM"}], stream=False)
    print(res)
