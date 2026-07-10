import logging
from typing import List, Dict, Any, Optional
import numpy as np
from app.config import settings
import openai

logger = logging.getLogger(__name__)

# Try to import qdrant_client, otherwise mock it
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logger.warning("qdrant-client not installed. Vector store will operate in fallback mode.")

class VectorStoreService:
    """Service for interacting with Qdrant vector database with in-memory fallback."""
    
    def __init__(self):
        self.settings = settings
        self.client = None
        self.fallback_mode = True
        self.fallback_db = {}  # In-memory mock database: {id: {"vector": [...], "metadata": ...}}
        self.vector_size = 1536  # Default dimension for text-embedding-ada-002 / text-embedding-3-small
        
        if QDRANT_AVAILABLE and self.settings.QDRANT_URL:
            try:
                # Initialize Qdrant Client
                if self.settings.QDRANT_URL.startswith("sqlite") or self.settings.QDRANT_URL == ":memory:":
                    self.client = QdrantClient(location=self.settings.QDRANT_URL)
                else:
                    self.client = QdrantClient(
                        url=self.settings.QDRANT_URL,
                        api_key=self.settings.QDRANT_API_KEY,
                        timeout=5
                    )
                
                # Test connection
                self.client.get_collections()
                self.fallback_mode = False
                logger.info(f"Connected to Qdrant at {self.settings.QDRANT_URL}")
                self._init_collection()
            except Exception as e:
                logger.warning(f"Failed to connect to Qdrant: {e}. Falling back to in-memory mode.")
                self.client = None
                self.fallback_mode = True

    def _init_collection(self):
        """Initialize the target collection in Qdrant."""
        if self.fallback_mode or not self.client:
            return
            
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.settings.QDRANT_COLLECTION_NAME not in collection_names:
                logger.info(f"Creating Qdrant collection: {self.settings.QDRANT_COLLECTION_NAME}")
                self.client.create_collection(
                    collection_name=self.settings.QDRANT_COLLECTION_NAME,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
                )
        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {e}")
            self.fallback_mode = True

    def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for the input text using OpenAI or fallback."""
        if not text:
            return [0.0] * self.vector_size
            
        # 1. Try OpenAI if configured
        if self.settings.OPENAI_API_KEY:
            try:
                client = openai.OpenAI(api_key=self.settings.OPENAI_API_KEY)
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"OpenAI embedding generation failed: {e}")
                
        # 2. Heuristic fallback embedding (deterministic mock vector based on text hash)
        import hashlib
        hash_val = hashlib.sha256(text.encode('utf-8')).digest()
        # Seed numpy generator with hash bytes to produce deterministic vector
        seed = int.from_bytes(hash_val[:4], byteorder='big')
        rng = np.random.default_rng(seed)
        vec = rng.normal(0, 1, self.vector_size)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def upsert_item(self, item_id: str, vector: List[float], metadata: dict) -> bool:
        """Upsert a research item's vector embedding into the store."""
        if len(vector) != self.vector_size:
            logger.warning(f"Vector size mismatch: expected {self.vector_size}, got {len(vector)}. Padding/cropping.")
            if len(vector) < self.vector_size:
                vector = vector + [0.0] * (self.vector_size - len(vector))
            else:
                vector = vector[:self.vector_size]
                
        if self.fallback_mode or not self.client:
            self.fallback_db[item_id] = {
                "vector": vector,
                "metadata": metadata
            }
            logger.debug(f"Upserted item {item_id} to in-memory vector store fallback")
            return True
            
        try:
            point = PointStruct(
                id=item_id,
                vector=vector,
                payload=metadata
            )
            self.client.upsert(
                collection_name=self.settings.QDRANT_COLLECTION_NAME,
                points=[point]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to upsert to Qdrant: {e}. Saving to in-memory fallback.")
            self.fallback_db[item_id] = {
                "vector": vector,
                "metadata": metadata
            }
            return True

    def search_similar(self, query_vector: List[float], limit: int = 5, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Search for items similar to query_vector exceeding relevance threshold."""
        if len(query_vector) != self.vector_size:
            if len(query_vector) < self.vector_size:
                query_vector = query_vector + [0.0] * (self.vector_size - len(query_vector))
            else:
                query_vector = query_vector[:self.vector_size]
                
        if self.fallback_mode or not self.client:
            results = []
            q_vec = np.array(query_vector)
            q_norm = np.linalg.norm(q_vec)
            
            for item_id, data in self.fallback_db.items():
                i_vec = np.array(data["vector"])
                i_norm = np.linalg.norm(i_vec)
                
                if q_norm > 0 and i_norm > 0:
                    similarity = float(np.dot(q_vec, i_vec) / (q_norm * i_norm))
                else:
                    similarity = 0.0
                    
                if similarity >= threshold:
                    results.append({
                        "id": item_id,
                        "score": similarity,
                        "payload": data["metadata"]
                    })
                    
            results = sorted(results, key=lambda x: x["score"], reverse=True)[:limit]
            return results
            
        try:
            search_results = self.client.search(
                collection_name=self.settings.QDRANT_COLLECTION_NAME,
                query_vector=query_vector,
                limit=limit,
                score_threshold=threshold
            )
            
            return [
                {
                    "id": str(res.id),
                    "score": res.score,
                    "payload": res.payload
                }
                for res in search_results
            ]
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}. Executing in-memory search fallback.")
            results = []
            q_vec = np.array(query_vector)
            q_norm = np.linalg.norm(q_vec)
            for item_id, data in self.fallback_db.items():
                i_vec = np.array(data["vector"])
                i_norm = np.linalg.norm(i_vec)
                similarity = float(np.dot(q_vec, i_vec) / (q_norm * i_norm)) if (q_norm > 0 and i_norm > 0) else 0.0
                if similarity >= threshold:
                    results.append({
                        "id": item_id,
                        "score": similarity,
                        "payload": data["metadata"]
                    })
            return sorted(results, key=lambda x: x["score"], reverse=True)[:limit]
