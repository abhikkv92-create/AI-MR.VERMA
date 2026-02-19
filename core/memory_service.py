import logging
import os
import time
from datetime import datetime
from typing import Any

import requests
from dotenv import load_dotenv
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

logger = logging.getLogger("Kernel.Memory")


class MemoryService:
    """
    Core service for Vector Memory using Milvus and NVIDIA Embeddings.
    Model: nvidia/nv-embedqa-e5-v5 (1024 dimensions)
    """

    COLLECTION_NAME = "mr_verma_memories"
    DIMENSION = 1024

    def __init__(self):
        load_dotenv()
        self.api_key = os.environ.get("NVIDIA_API_KEY")
        self.milvus_host = os.environ.get("MILVUS_HOST", "localhost")
        self.milvus_port = os.environ.get("MILVUS_PORT", "19530")
        self.connected = False
        self.collection = None

    def connect(self):
        """Connect to Milvus and initialize the collection."""
        try:
            logger.info(
                f"Connecting to Milvus at {self.milvus_host}:{self.milvus_port}..."
            )
            connections.connect(
                alias="default", host=self.milvus_host, port=self.milvus_port
            )
            self.connected = True
            self._ensure_collection()
            logger.info("MemoryService successfully connected to Milvus.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            return False

    def _ensure_collection(self):
        """Creates or loads the memory collection."""
        if not self.connected:
            return

        if utility.has_collection(self.COLLECTION_NAME):
            self.collection = Collection(self.COLLECTION_NAME)
            self.collection.load()
            return

        # Define Schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.DIMENSION),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.JSON),
            FieldSchema(name="timestamp", dtype=DataType.INT64),
        ]
        schema = CollectionSchema(fields, description="MR.VERMA Semantic Memory")
        self.collection = Collection(name=self.COLLECTION_NAME, schema=schema)

        # Create Index (HNSW for production-grade search)
        index_params = {
            "index_type": "HNSW",
            "metric_type": "L2",
            "params": {"M": 16, "efConstruction": 128},
        }
        self.collection.create_index(field_name="vector", index_params=index_params)
        self.collection.load()
        logger.info(f"Collection '{self.COLLECTION_NAME}' created and loaded.")

    def _get_embedding(self, text: str) -> list:
        """Fetch embedding from NVIDIA API."""
        if not self.api_key:
            logger.error("NVIDIA_API_KEY not found in environment.")
            return []

        url = "https://integrate.api.nvidia.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "input": [text],
            "model": "nvidia/nv-embedqa-e5-v5",
            "input_type": "query" if "query" in text.lower() else "passage",
            "encoding_format": "float",
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code != 200:
                logger.error(
                    f"Embedding API error: {response.status_code} - {response.text}"
                )
                return []
            vector = response.json()["data"][0]["embedding"]
            logger.debug(f"Received embedding with dimension: {len(vector)}")
            return vector
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return []

    async def store(self, content: str, metadata: dict = {}) -> bool:
        """Store a text snippet in the vector database."""
        if not self.connected:
            self.connect()

        vector = self._get_embedding(content)
        if not vector:
            return False

        data = [[vector], [content], [metadata], [int(time.time())]]

        try:
            # Check vector dimension vs expected
            if len(vector) != self.DIMENSION:
                logger.error(
                    f"Dimension mismatch! Expected {self.DIMENSION}, got {len(vector)}"
                )
                return False

            self.collection.insert(data)
            logger.info("Memory stored successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to store memory in Milvus: {e}")
            return False

    async def store_visual_memory(
        self, description: str, image_path: str, query: str = ""
    ) -> bool:
        """Specialized storage for visual analysis results."""
        metadata = {
            "type": "visual",
            "source": image_path,
            "query": query,
            "timestamp_iso": datetime.now().isoformat(),
        }
        content = f"Visual Analysis of {os.path.basename(image_path)}: {description}"
        return await self.store(content, metadata)

    async def recall(self, query: str, engine: Any, context_window: int = 5) -> str:
        """
        Cognitive Recall: Searches, filters, and synthesizes memories using the Primary Engine.
        This provides a 'narrative summary' of past relevant events.
        """
        logger.info(f"Initiating Neural Recall for: '{query}'")
        raw_memories = await self.search(query, limit=context_window)

        if not raw_memories:
            return "No relevant past memories found."

        # Synthesize memories into a cognitive summary
        memory_text = "\n".join(
            [
                f"- [{m['metadata'].get('type', 'generic')}] {m['content']}"
                for m in raw_memories
            ]
        )

        system_prompt = (
            "You are the MR.VERMA Neural Recall Module. "
            "Synthesize the provided memories into a concise 'Cognitive Summary' relevant to the current query. "
            "Filter out noise. Focus on lessons learned and previous solutions."
        )

        try:
            completion = engine.generate(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Query: {query}\n\nMemories:\n{memory_text}",
                    },
                ],
                stream=False,
            )
            recall_summary = completion.choices[0].message.content
            logger.info("Neural Recall Synthesis Complete.")
            return recall_summary
        except Exception as e:
            logger.error(f"Recall Synthesis Failed: {e}")
            return f"Raw Recall: {memory_text[:200]}..."

    async def get_temporal_context(self, minutes_ago: int = 60) -> list:
        """Retrieves memories within a specific time window."""
        if not self.connected:
            self.connect()

        start_time = int(time.time()) - (minutes_ago * 60)
        expr = f"timestamp > {start_time}"

        try:
            results = self.collection.query(
                expr=expr, output_fields=["content", "metadata", "timestamp"], limit=10
            )
            return results
        except Exception as e:
            logger.error(f"Temporal retrieval failed: {e}")
            return []


# Singleton instance
memory_service = MemoryService()
