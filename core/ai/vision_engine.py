import base64
import json
import logging
import os
import sys
from typing import Any, List

import requests

# Configure Logging
logger = logging.getLogger("AI.VisionEngine")

class VisionAIEngine:
    """
    Vision Engine for analyzing images and videos using NVIDIA's Nemotron-4 340B Vision model.
    """
    def __init__(self):
        # Default key provided by user, can be overridden by env var
        self.api_key = os.environ.get("NVIDIA_API_KEY_VISION")
        self.invoke_url = os.environ.get("NVIDIA_API_URL_VISION", "https://integrate.api.nvidia.com/v1/chat/completions")
        self.model = "nvidia/nemotron-nano-12b-v2-vl"

        # Supported media types
        self.kSupportedList = {
            "png": ["image/png", "image_url"],
            "jpg": ["image/jpeg", "image_url"],
            "jpeg": ["image/jpeg", "image_url"],
            "webp": ["image/webp", "image_url"],
            "mp4": ["video/mp4", "video_url"],
            "webm": ["video/webm", "video_url"],
            "mov": ["video/mov", "video_url"]
        }

        if not self.api_key:
             logger.warning("NVIDIA_API_KEY_VISION not set and no default key found. Vision engine disabled.")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def _get_extension(self, filename: str) -> str:
        _, ext = os.path.splitext(filename)
        return ext[1:].lower()

    def _mime_type(self, ext: str) -> str:
        return self.kSupportedList[ext][0]

    def _media_type(self, ext: str) -> str:
        return self.kSupportedList[ext][1]

    def _encode_media_base64(self, media_file: str) -> str:
        """Encode media file to base64 string"""
        try:
            with open(media_file, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to encode media file {media_file}: {e}")
            raise

    def analyze(self, media_files: List[str], query: str = "Describe the scene", stream: bool = False) -> Any:
        """
        Analyzes the provided media files (images/videos) with the given query.
        """
        if not self.is_available():
             raise ValueError("Vision Engine is not configured.")

        # If single string passed, convert to list
        if isinstance(media_files, str):
            media_files = [media_files]

        assert isinstance(media_files, list), f"media_files must be a list, got {type(media_files)}"

        has_video = False
        content = [{"type": "text", "text": query}]

        if not media_files:
             # Text only fallback, though this engine is for vision
             pass
        else:
            for media_file in media_files:
                if not os.path.exists(media_file):
                    logger.error(f"Media file not found: {media_file}")
                    continue

                ext = self._get_extension(media_file)
                if ext not in self.kSupportedList:
                    logger.warning(f"Unsupported format {ext} for file {media_file}. Skipping.")
                    continue

                media_type_key = self._media_type(ext)
                if media_type_key == "video_url":
                    has_video = True

                try:
                    base64_data = self._encode_media_base64(media_file)

                    media_obj = {
                        "type": media_type_key,
                        media_type_key: {
                            "url": f"data:{self._mime_type(ext)};base64,{base64_data}"
                        }
                    }
                    content.append(media_obj)
                except Exception as e:
                    logger.error(f"Error processing {media_file}: {e}")

            if has_video and len(media_files) > 1:
                 # API restriction mentioned in user snippet: "Only single video supported."
                 # However, we will let the API handle validation or warn here.
                 if len([f for f in media_files if self._media_type(self._get_extension(f)) == "video_url"]) > 1:
                     logger.warning("Multiple videos detected. The API might only support one video per request.")


        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream" if stream else "application/json"
        }

        # System prompt logic
        system_prompt = "/think" # Defaulting to /think for now as per snippet

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": content,
            }
        ]

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "temperature": 0.3,
            "top_p": 0.85,
            "frequency_penalty": 0.2,
            "presence_penalty": 0.15,
            "messages": messages,
            "stream": stream
        }

        try:
            response = requests.post(self.invoke_url, headers=headers, json=payload, stream=stream, timeout=120)

            if response.status_code != 200:
                logger.error(f"Vision Engine Error {response.status_code}: {response.text}")
                return f"Error: {response.text}"

            if stream:
                # Basic stream handler - similar to secondary engine
                return self._stream_generator(response)
            else:
                return response.json()["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Vision Request failed: {e}")
            return f"Error: {e!s}"

    def _stream_generator(self, response):
        for line in response.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                # Remove "data: " prefix
                if decoded.startswith("data: "):
                    decoded = decoded[6:]

                if decoded.strip() == "[DONE]":
                    break

                try:
                    chunk = json.loads(decoded)
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                         delta = chunk["choices"][0].get("delta", {})
                         if "content" in delta:
                             yield delta["content"]
                except:
                    pass

if __name__ == "__main__":
    # Test block
    logging.basicConfig(level=logging.INFO)
    engine = VisionAIEngine()
    if len(sys.argv) > 1:
        files = sys.argv[1:]
        print(f"Analyzing {files}...")
        result = engine.analyze(files, stream=False)
        print("Result:", result)
    else:
        print("Provide image/video paths as arguments to test.")
