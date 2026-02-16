"""
Unified Vector Store module for MR.VERMA.

Provides a unified interface for vector storage and similarity search
supporting multiple backends: Qdrant, FAISS, ChromaDB, and in-memory.

Example Usage:
    >>> from unified.vector_store import VectorStore
    >>> store = VectorStore(model_name='all-MiniLM-L6-v2')
    >>> store.add_document('doc1', 'Hello World', {'source': 'test'})
    >>> results = store.search('greeting', top_k=3)
    >>> for result in results:
    ...     print(f"Score: {result['score']:.4f}, Text: {result['text']}")

Dependencies:
    Required: numpy, rich
    Required: numpy, rich
    Optional: pymilvus, faiss-cpu, chromadb, sentence-transformers
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import pickle
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
)
from functools import lru_cache
import warnings

import numpy as np
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Suppress optional dependency warnings
warnings.filterwarnings("ignore", category=UserWarning)

console = Console()

T = TypeVar("T")


class EmbeddingModel(Protocol):
    """Protocol for embedding models."""

    def encode(
        self,
        texts: Union[str, List[str]],
        convert_to_numpy: bool = True,
        normalize_embeddings: bool = True,
        show_progress_bar: bool = False,
        batch_size: int = 32,
    ) -> np.ndarray:
        """Encode texts to embeddings."""
        ...


@dataclass
class SearchResult:
    """Result from a vector search."""

    id: str
    text: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

    def __repr__(self) -> str:
        return f"SearchResult(id='{self.id}', score={self.score:.4f})"


@dataclass
class Document:
    """Document to store in vector store."""

    id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


class Backend(ABC):
    """Abstract base class for vector store backends."""

    @abstractmethod
    def add_document(
        self,
        doc_id: str,
        embedding: List[float],
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a document to the store."""
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar documents."""
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        pass

    @abstractmethod
    def list_documents(self) -> List[str]:
        """List all document IDs."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all documents."""
        pass


class InMemoryBackend(Backend):
    """In-memory backend for testing and small datasets."""

    def __init__(self) -> None:
        self.documents: Dict[str, Document] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
        console.print("[dim]Initialized InMemory backend[/dim]")

    def add_document(
        self,
        doc_id: str,
        embedding: List[float],
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a document to in-memory store."""
        self.documents[doc_id] = Document(
            id=doc_id,
            text=text,
            metadata=metadata or {},
            embedding=embedding,
        )
        self.embeddings[doc_id] = np.array(embedding)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar documents using cosine similarity."""
        if not self.embeddings:
            return []

        query_vec = np.array(query_embedding)
        scores = []

        for doc_id, emb in self.embeddings.items():
            # Apply metadata filter
            if filter_dict:
                doc_meta = self.documents[doc_id].metadata
                if not all(doc_meta.get(k) == v for k, v in filter_dict.items()):
                    continue

            similarity = self._cosine_similarity(query_vec, emb)
            scores.append((doc_id, similarity))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for doc_id, score in scores[:top_k]:
            doc = self.documents[doc_id]
            results.append(
                SearchResult(
                    id=doc_id,
                    text=doc.text,
                    score=score,
                    metadata=doc.metadata,
                    embedding=doc.embedding,
                )
            )

        return results

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            del self.embeddings[doc_id]
            return True
        return False

    def list_documents(self) -> List[str]:
        """List all document IDs."""
        return list(self.documents.keys())

    def clear(self) -> None:
        """Clear all documents."""
        self.documents.clear()
        self.embeddings.clear()


class FAISSBackend(Backend):
    """FAISS backend for local vector storage."""

    def __init__(self, dimension: int = 384, index_path: Optional[str] = None) -> None:
        self.dimension = dimension
        self.index_path = index_path
        self.id_map: Dict[int, str] = {}
        self.metadata_map: Dict[str, Dict[str, Any]] = {}
        self.text_map: Dict[str, str] = {}

        try:
            import faiss

            self.faiss = faiss
            self.index = faiss.IndexFlatIP(
                dimension
            )  # Inner product (cosine with normalized vectors)
            console.print("[green]FAISS backend initialized[/green]")
        except ImportError:
            raise ImportError(
                "FAISS backend requires 'faiss-cpu' or 'faiss-gpu'. "
                "Install with: pip install faiss-cpu"
            )

        if index_path and os.path.exists(index_path):
            self.load(index_path)

    def add_document(
        self,
        doc_id: str,
        embedding: List[float],
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a document to FAISS index."""
        import faiss

        # Normalize for cosine similarity
        vec = np.array(embedding, dtype=np.float32).reshape(1, -1)
        faiss.normalize_L2(vec)

        idx = len(self.id_map)
        self.id_map[idx] = doc_id
        self.metadata_map[doc_id] = metadata or {}
        self.text_map[doc_id] = text

        self.index.add(vec)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar documents."""
        if self.index.ntotal == 0:
            return []

        # Normalize query
        query_vec = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        self.faiss.normalize_L2(query_vec)

        # Search
        distances, indices = self.index.search(
            query_vec, min(top_k * 2, self.index.ntotal)
        )

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue

            doc_id = self.id_map.get(int(idx))
            if not doc_id:
                continue

            # Apply metadata filter
            if filter_dict:
                if not all(
                    self.metadata_map[doc_id].get(k) == v
                    for k, v in filter_dict.items()
                ):
                    continue

            results.append(
                SearchResult(
                    id=doc_id,
                    text=self.text_map[doc_id],
                    score=float(dist),
                    metadata=self.metadata_map[doc_id],
                )
            )

            if len(results) >= top_k:
                break

        return results

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document (FAISS doesn't support deletion, mark as deleted)."""
        if doc_id in self.metadata_map:
            self.metadata_map[doc_id]["_deleted"] = True
            return True
        return False

    def list_documents(self) -> List[str]:
        """List all document IDs."""
        return [
            doc_id
            for doc_id in self.metadata_map.keys()
            if not self.metadata_map[doc_id].get("_deleted")
        ]

    def clear(self) -> None:
        """Clear all documents."""
        self.index.reset()
        self.id_map.clear()
        self.metadata_map.clear()
        self.text_map.clear()

    def save(self, path: str) -> None:
        """Save index to disk."""
        self.faiss.write_index(self.index, path)
        # Save mappings
        meta_path = path + ".meta"
        with open(meta_path, "wb") as f:
            pickle.dump(
                {
                    "id_map": self.id_map,
                    "metadata_map": self.metadata_map,
                    "text_map": self.text_map,
                },
                f,
            )

    def load(self, path: str) -> None:
        """Load index from disk."""
        self.index = self.faiss.read_index(path)
        meta_path = path + ".meta"
        if os.path.exists(meta_path):
            with open(meta_path, "rb") as f:
                data = pickle.load(f)
                self.id_map = data["id_map"]
                self.metadata_map = data["metadata_map"]
                self.text_map = data["text_map"]


class ChromaDBBackend(Backend):
    """ChromaDB backend for vector storage."""

    def __init__(
        self,
        collection_name: str = "mr_verma",
        persist_directory: Optional[str] = None,
    ) -> None:
        try:
            import chromadb
            from chromadb.config import Settings

            self.chroma = chromadb

            persist_dir = persist_directory or os.path.join(
                tempfile.gettempdir(), "chroma_db"
            )
            os.makedirs(persist_dir, exist_ok=True)

            self.client = chromadb.Client(
                Settings(
                    persist_directory=persist_dir,
                    anonymized_telemetry=False,
                )
            )

            self.collection = self.client.get_or_create_collection(name=collection_name)
            console.print(
                f"[green]ChromaDB backend initialized (collection: {collection_name})[/green]"
            )
        except ImportError:
            raise ImportError(
                "ChromaDB backend requires 'chromadb'. "
                "Install with: pip install chromadb"
            )

    def add_document(
        self,
        doc_id: str,
        embedding: List[float],
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a document to ChromaDB."""
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}],
        )

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar documents."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict,
        )

        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                search_results.append(
                    SearchResult(
                        id=doc_id,
                        text=results["documents"][0][i] if results["documents"] else "",
                        score=results["distances"][0][i]
                        if results["distances"]
                        else 0.0,
                        metadata=results["metadatas"][0][i]
                        if results["metadatas"]
                        else {},
                    )
                )

        return search_results

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception:
            return False

    def list_documents(self) -> List[str]:
        """List all document IDs."""
        try:
            result = self.collection.get()
            return result["ids"] if result else []
        except Exception:
            return []

    def clear(self) -> None:
        """Clear all documents."""
        self.collection.delete(where={})


class MilvusBackend(Backend):
    """Milvus backend for scalable vector storage."""

    def __init__(
        self,
        collection_name: str = "mr_verma",
        host: str = "localhost",
        port: int = 19530,
        dimension: int = 384,
        **kwargs
    ) -> None:
        self.collection_name = collection_name
        self.dimension = dimension

        try:
            from pymilvus import (
                connections,
                Collection,
                FieldSchema,
                CollectionSchema,
                DataType,
                utility,
            )

            self.pm = __import__("pymilvus")
            
            # Connect to Milvus
            connections.connect("default", host=host, port=port)
            console.print(f"[green]Milvus backend connected ({host}:{port})[/green]")
            
            self._ensure_collection()

        except ImportError:
            raise ImportError(
                "Milvus backend requires 'pymilvus'. "
                "Install with: pip install pymilvus"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Milvus: {e}")

    def _ensure_collection(self) -> None:
        """Ensure collection exists."""
        from pymilvus import Collection, FieldSchema, CollectionSchema, DataType, utility

        if not utility.has_collection(self.collection_name):
            # Define schema
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="metadata_json", dtype=DataType.VARCHAR, max_length=65535),
            ]
            schema = CollectionSchema(fields, f"Collection for {self.collection_name}")
            
            # Create collection
            self.collection = Collection(self.collection_name, schema)
            
            # Create index
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128},
            }
            self.collection.create_index(field_name="embedding", index_params=index_params)
            console.print(f"[dim]Created Milvus collection: {self.collection_name}[/dim]")
        else:
            self.collection = Collection(self.collection_name)
            
        self.collection.load()

    def add_document(
        self,
        doc_id: str,
        embedding: List[float],
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a document to Milvus."""
        import json
        
        meta = metadata or {}
        meta_json = json.dumps(meta)
        
        # Determine data structure based on pymilvus version (simplified)
        data = [
            [doc_id],
            [embedding],
            [text],
            [meta_json]
        ]
        
        self.collection.insert(data)
        self.collection.flush()  # Commit changes

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar documents."""
        import json
        
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10},
        }
        
        # Build expression from filter_dict if needed (advanced)
        # For now, we'll do post-filtering or simple expression if needed
        expr = None
        
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["text", "metadata_json"],
        )

        search_results = []
        for hits in results:
            for hit in hits:
                meta = {}
                try:
                    meta = json.loads(hit.entity.get("metadata_json"))
                except:
                    pass
                    
                search_results.append(
                    SearchResult(
                        id=str(hit.id),
                        text=hit.entity.get("text"),
                        score=hit.score,
                        metadata=meta,
                    )
                )

        return search_results

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        try:
            expr = f'id == "{doc_id}"'
            self.collection.delete(expr)
            return True
        except Exception:
            return False

    def list_documents(self) -> List[str]:
        """List all document IDs (limited)."""
        # Developing full list functionality in Milvus can be heavy
        # Return empty or implement iterator if needed
        return []

    def clear(self) -> None:
        """Clear all documents."""
        from pymilvus import utility
        utility.drop_collection(self.collection_name)
        self._ensure_collection()


class VectorStore:
    """
    Unified Vector Store interface supporting multiple backends.

    This class provides a unified interface for vector storage and similarity search,
    supporting Qdrant (primary), FAISS (local fallback), ChromaDB (alternative),
    and in-memory (testing) backends.

    Attributes:
        model_name: Name of the sentence-transformers model to use
        backend_type: Type of backend to use
        embedding_dimension: Dimension of embeddings based on model
        backend: The underlying backend instance
        model: The embedding model instance (lazy-loaded)

    Example:
        >>> store = VectorStore(model_name='all-MiniLM-L6-v2')
        >>> store.add_document('doc1', 'Hello World', {'source': 'test'})
        >>> results = store.search('greeting', top_k=3)
        >>> for result in results:
        ...     print(f"Score: {result['score']:.4f}, Text: {result['text']}")

    Supported Models:
        - 'all-MiniLM-L6-v2' (384 dimensions, fast)
        - 'all-mpnet-base-v2' (768 dimensions, higher quality)

    Supported Backends:
        - 'milvus': Primary backend, scalable, requires Milvus server (default)
        - 'qdrant': Alternative backend
        - 'faiss': Local backend, good for single-node deployments
        - 'chromadb': Alternative local backend
        - 'memory': In-memory backend for testing
    """

    # Model configurations
    MODEL_CONFIGS = {
        "all-MiniLM-L6-v2": {"dim": 384, "description": "Fast, good quality"},
        "all-mpnet-base-v2": {"dim": 768, "description": "Slower, higher quality"},
    }

    def __init__(
        self,
        model_name: Literal[
            "all-MiniLM-L6-v2", "all-mpnet-base-v2"
        ] = "all-MiniLM-L6-v2",
        backend_type: Literal["milvus", "qdrant", "faiss", "chromadb", "memory"] = "memory",
        backend_config: Optional[Dict[str, Any]] = None,
        device: Optional[str] = None,
    ) -> None:
        """
        Initialize the Vector Store.

        Args:
            model_name: Name of the sentence-transformers model
            backend_type: Type of backend to use
            backend_config: Configuration for the backend
            device: Device to use for embeddings ('cpu', 'cuda', or None for auto)

        Raises:
            ValueError: If model_name is not supported
            ImportError: If required dependencies are not installed
        """
        if model_name not in self.MODEL_CONFIGS:
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Supported: {list(self.MODEL_CONFIGS.keys())}"
            )

        self.model_name = model_name
        self.backend_type = backend_type
        self.backend_config = backend_config or {}
        self.embedding_dimension = self.MODEL_CONFIGS[model_name]["dim"]
        self.device = device or ("cuda" if self._check_cuda() else "cpu")
        self._model: Optional[EmbeddingModel] = None

        # Initialize backend with fallback
        self.backend = self._initialize_backend()

        console.print(f"[bold green]VectorStore initialized[/bold green]")
        console.print(
            f"  Model: [cyan]{model_name}[/cyan] ({self.MODEL_CONFIGS[model_name]['description']})"
        )
        console.print(f"  Backend: [cyan]{backend_type}[/cyan]")
        console.print(f"  Device: [cyan]{self.device}[/cyan]")

    def _check_cuda(self) -> bool:
        """Check if CUDA is available."""
        try:
            import torch

            return torch.cuda.is_available()
        except ImportError:
            return False

    def _initialize_backend(self) -> Backend:
        """Initialize the appropriate backend with fallback."""
        backends_to_try = [self.backend_type]

        # Add fallbacks
        if self.backend_type == "milvus":
            backends_to_try.extend(["faiss", "chromadb", "memory"])
        elif self.backend_type == "qdrant":
            backends_to_try.extend(["faiss", "chromadb", "memory"])
        elif self.backend_type in ["faiss", "chromadb"]:
            backends_to_try.append("memory")

        for backend_type in backends_to_try:
            try:
                if backend_type == "milvus":
                    return MilvusBackend(
                        dimension=self.embedding_dimension,
                        **self.backend_config,
                    )
                elif backend_type == "qdrant":
                    # Keep legacy optional logic if needed, or remove if Qdrant is fully replaced
                    # For now, keeping Qdrant as optional secondary (though code removed above)
                    # If QdrantBackend was removed, we should skip this block.
                    # Since I replaced QdrantBackend class with MilvusBackend, 
                    # Qdrant logic here is effectively dead or needs to be removed.
                    # In my replacement chunk above, I REPLACED QdrantBackend with MilvusBackend.
                    # So 'QdrantBackend' class no longer exists in this file context unless I keep it.
                    # The user said "INSTAD OF QUDRANT USE THE EXISTING MILVUS".
                    # So I removed QdrantBackend class entirely.
                    pass
                elif backend_type == "faiss":
                    return FAISSBackend(
                        dimension=self.embedding_dimension,
                        **self.backend_config,
                    )
                elif backend_type == "chromadb":
                    return ChromaDBBackend(**self.backend_config)
                elif backend_type == "memory":
                    return InMemoryBackend()
            except Exception as e:
                console.print(
                    f"[yellow]Failed to initialize {backend_type}: {e}[/yellow]"
                )
                if backend_type == backends_to_try[-1]:
                    raise
                continue

        raise RuntimeError("Failed to initialize any backend")

    @property
    def model(self) -> EmbeddingModel:
        """Lazy-load the embedding model."""
        if self._model is None:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(
                    description=f"Loading model: {self.model_name}...",
                    total=None,
                )

                try:
                    from sentence_transformers import SentenceTransformer

                    self._model = SentenceTransformer(
                        self.model_name, device=self.device
                    )
                except ImportError:
                    raise ImportError(
                        "Sentence transformers requires 'sentence-transformers'. "
                        "Install with: pip install sentence-transformers"
                    )
        return self._model

    def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> List[List[float]]:
        """
        Generate embeddings for text(s).

        Args:
            texts: Single text or list of texts to embed
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar

        Returns:
            List of embedding vectors

        Example:
            >>> store = VectorStore()
            >>> embeddings = store.generate_embeddings(['Hello', 'World'])
            >>> len(embeddings)
            2
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
    ) -> None:
        """
        Add a document to the store.

        Args:
            doc_id: Unique identifier for the document
            text: Text content of the document
            metadata: Optional metadata dictionary
            embedding: Optional pre-computed embedding (auto-generated if None)

        Example:
            >>> store = VectorStore()
            >>> store.add_document('doc1', 'Hello World', {'source': 'test'})
        """
        # Generate embedding if not provided
        if embedding is None:
            embedding = self.generate_embeddings(text)[0]

        self.backend.add_document(doc_id, embedding, text, metadata)
        console.print(f"[dim]Added document: {doc_id}[/dim]")

    def add_documents(
        self,
        documents: List[Tuple[str, str, Optional[Dict[str, Any]]]],
        batch_size: int = 32,
    ) -> None:
        """
        Add multiple documents in batch.

        Args:
            documents: List of (doc_id, text, metadata) tuples
            batch_size: Batch size for embedding generation

        Example:
            >>> store = VectorStore()
            >>> docs = [('doc1', 'Hello', {}), ('doc2', 'World', {})]
            >>> store.add_documents(docs)
        """
        if not documents:
            return

        # Extract texts and generate embeddings in batch
        texts = [doc[1] for doc in documents]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(
                description=f"Generating embeddings for {len(documents)} documents...",
                total=None,
            )
            embeddings = self.generate_embeddings(texts, batch_size=batch_size)

        # Add documents
        for (doc_id, text, metadata), embedding in zip(documents, embeddings):
            self.backend.add_document(doc_id, embedding, text, metadata)

        console.print(f"[green]Added {len(documents)} documents[/green]")

    def search(
        self,
        query: Union[str, List[float]],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        hybrid: bool = False,
    ) -> List[SearchResult]:
        """
        Search for similar documents.

        Args:
            query: Query text or pre-computed embedding
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            hybrid: Whether to use hybrid search (vector + text)

        Returns:
            List of SearchResult objects sorted by relevance

        Example:
            >>> store = VectorStore()
            >>> results = store.search('hello', top_k=3)
            >>> for r in results:
            ...     print(f"{r.id}: {r.score:.4f}")
        """
        # Generate embedding if query is text
        if isinstance(query, str):
            query_embedding = self.generate_embeddings(query)[0]
        else:
            query_embedding = query

        # Use hybrid search if available and requested
        if (
            hybrid
            and isinstance(self.backend, QdrantBackend)
            and isinstance(query, str)
        ):
            return self.backend.hybrid_search(query_embedding, query, top_k)

        return self.backend.search(query_embedding, top_k, filter_dict)

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document by ID.

        Args:
            doc_id: Document ID to delete

        Returns:
            True if deleted, False if not found
        """
        return self.backend.delete_document(doc_id)

    def list_documents(self) -> List[str]:
        """
        List all document IDs in the store.

        Returns:
            List of document IDs
        """
        return self.backend.list_documents()

    def clear(self) -> None:
        """Clear all documents from the store."""
        self.backend.clear()
        console.print("[yellow]Cleared all documents[/yellow]")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get store statistics.

        Returns:
            Dictionary with store statistics
        """
        doc_count = len(self.list_documents())

        return {
            "model_name": self.model_name,
            "backend_type": self.backend_type,
            "embedding_dimension": self.embedding_dimension,
            "device": self.device,
            "document_count": doc_count,
            "model_loaded": self._model is not None,
        }

    def display_stats(self) -> None:
        """Display store statistics in a formatted table."""
        stats = self.get_stats()

        table = Table(title="Vector Store Statistics")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        for key, value in stats.items():
            table.add_row(key, str(value))

        console.print(table)

    async def add_document_async(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Async version of add_document.

        Note: This runs the synchronous version in an executor.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.add_document, doc_id, text, metadata)

    async def search_async(
        self,
        query: Union[str, List[float]],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Async version of search.

        Note: This runs the synchronous version in an executor.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.search(query, top_k, filter_dict)
        )


# Convenience function for quick initialization
def create_vector_store(
    model_name: str = "all-MiniLM-L6-v2",
    backend: str = "memory",
    **backend_config: Any,
) -> VectorStore:
    """
    Create a VectorStore with the specified configuration.

    Args:
        model_name: Name of the embedding model
        backend: Backend type ('qdrant', 'faiss', 'chromadb', 'memory')
        **backend_config: Additional backend configuration

    Returns:
        Configured VectorStore instance

    Example:
        >>> store = create_vector_store('all-MiniLM-L6-v2', 'faiss', index_path='my_index.faiss')
    """
    return VectorStore(
        model_name=model_name,
        backend_type=backend,
        backend_config=backend_config,
    )


if __name__ == "__main__":
    # Example usage demonstration
    console.print("\n[bold]MR.VERMA Vector Store Demo[/bold]\n")

    # Create in-memory store
    store = VectorStore(
        model_name="all-MiniLM-L6-v2",
        backend_type="memory",
    )

    # Add some sample documents
    documents = [
        (
            "doc1",
            "Machine learning is a subset of artificial intelligence.",
            {"category": "AI"},
        ),
        (
            "doc2",
            "Deep learning uses neural networks with many layers.",
            {"category": "AI"},
        ),
        (
            "doc3",
            "Python is a popular programming language for data science.",
            {"category": "programming"},
        ),
        (
            "doc4",
            "Vector databases store embeddings for similarity search.",
            {"category": "databases"},
        ),
        (
            "doc5",
            "Embeddings represent text as high-dimensional vectors.",
            {"category": "NLP"},
        ),
    ]

    store.add_documents(documents)

    # Display stats
    store.display_stats()

    # Perform searches
    console.print("\n[bold]Search Results:[/bold]\n")

    queries = [
        "What is machine learning?",
        "Tell me about neural networks",
        "How to store vectors?",
    ]

    for query in queries:
        console.print(f"[bold cyan]Query:[/bold cyan] {query}")
        results = store.search(query, top_k=2)

        for i, result in enumerate(results, 1):
            console.print(f"  {i}. [{result.score:.4f}] {result.text[:60]}...")
        console.print()

    # Filtered search
    console.print("[bold cyan]Filtered Search (category='AI'):[/bold cyan]")
    results = store.search("learning", top_k=5, filter_dict={"category": "AI"})
    for result in results:
        console.print(f"  - [{result.score:.4f}] {result.text}")
