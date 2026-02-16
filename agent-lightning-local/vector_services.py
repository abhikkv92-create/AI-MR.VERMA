
import logging
import os
import time

import requests
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

log = logging.getLogger(__name__)

# ── Configuration ──
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus-standalone")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nvidia/nv-embed-v1")
EMBEDDING_URL = "https://integrate.api.nvidia.com/v1/embeddings"
COLLECTION_NAME = "verma_memory_v2"
DIMENSION = 4096 # nv-embed-v1 returns 4096

class EmbeddingService:
    """Service to generate vector embeddings using NVIDIA API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def get_embedding(self, text: str) -> list:
        """Generate a 1024-dimensional embedding for the given text."""
        if not self.api_key:
            log.warning("Embedding skipped: No NVIDIA_API_KEY")
            return []

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "input": [text],
            "model": EMBEDDING_MODEL,
            "input_type": "query",
            "encoding_format": "float"
        }

        try:
            resp = self.session.post(EMBEDDING_URL, headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            log.error(f"Embedding generation failed: {e}")
            return []

class MilvusService:
    """Service to manage Milvus collections and data ingestion."""

    def __init__(self):
        self._connected = False
        self.collection = None

    def connect(self):
        """Establish connection to Milvus and initialize collection."""
        try:
            log.info(f"Connecting to Milvus at {MILVUS_HOST}:{MILVUS_PORT}...")
            connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
            self._connected = True
            self._init_collection()
            log.info("Milvus initialized successfully.")
        except Exception as e:
            log.error(f"Milvus connection failed: {e}")

    def _init_collection(self):
        """Create collection if it doesn't exist, define schema, and create index."""
        if not self._connected: return

        if utility.has_collection(COLLECTION_NAME):
            self.collection = Collection(COLLECTION_NAME)
            self.collection.load()
            return

        # Define Schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="role", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="timestamp", dtype=DataType.INT64),
            FieldSchema(name="session_id", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="telemetry", dtype=DataType.JSON)
        ]
        schema = CollectionSchema(fields, description="MR.VERMA Vector Memory")
        self.collection = Collection(name=COLLECTION_NAME, schema=schema)

        # Create Index (HNSW for performance)
        index_params = {
            "index_type": "HNSW",
            "metric_type": "L2",
            "params": {"M": 8, "efConstruction": 64}
        }
        self.collection.create_index(field_name="vector", index_params=index_params)
        self.collection.load()
        log.info(f"Collection '{COLLECTION_NAME}' created and indexed.")

    def ingest(self, vector: list, content: str, role: str, session_id: str, telemetry: dict):
        """Insert a new interaction into Milvus."""
        if not self._connected or not self.collection:
            log.warning("Ingestion skipped: Milvus not connected.")
            return

        data = [
            [vector],
            [content],
            [role],
            [int(time.time())],
            [session_id],
            [telemetry]
        ]
        try:
            self.collection.insert(data)
            # No need to flush every time in production, Milvus manages it.
            log.debug("Ingested interaction into Milvus.")
        except Exception as e:
            log.error(f"Ingestion failed: {e}")

    def search(self, vector: list, limit: int = 5) -> list:
        """Search for top-K most relevant interactions."""
        if not self._connected or not self.collection:
            return []

        search_params = {"metric_type": "L2", "params": {"ef": 64}}
        try:
            results = self.collection.search(
                data=[vector],
                anns_field="vector",
                param=search_params,
                limit=limit,
                output_fields=["content", "role", "timestamp"]
            )
            return results[0] # Returns top results for the single query vector
        except Exception as e:
            log.error(f"Milvus search failed: {e}")
            return []
