import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
import logging

logger = logging.getLogger(__name__)

class RAGVectorStore:
    """
    Manages vector embeddings and retrieval against Qdrant collections.
    Includes memory fallback database for offline development setups.
    """
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "factcheck_kb"):
        self.collection_name = collection_name
        self.host = os.getenv("QDRANT_HOST", host)
        self.port = int(os.getenv("QDRANT_PORT", port))
        
        # Load SentenceTransformer for text embedding
        try:
            self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer: {str(e)}. Using fallback bag-of-words encoder.")
            self.embedder = None

        # Connect to Qdrant
        try:
            self.client = QdrantClient(host=self.host, port=self.port, timeout=3.0)
            self._init_collection()
            self.use_qdrant = True
            logger.info(f"Connected to Qdrant at {self.host}:{self.port}")
        except Exception as e:
            logger.warning(f"Failed to connect to Qdrant: {str(e)}. Using local in-memory RAG fallback.")
            self.use_qdrant = False
            self.fallback_db = []

    def _init_collection(self):
        # Create collection if it doesn't exist
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=384, # all-MiniLM-L6-v2 embedding size
                    distance=qmodels.Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {self.collection_name}")

    def _get_embedding(self, text: str) -> list:
        if self.embedder:
            return self.embedder.encode(text).tolist()
        else:
            # Fallback bag-of-words mock vector (length 384)
            vec = [0.0] * 384
            for i, char in enumerate(text[:384]):
                vec[i] = float(ord(char)) / 255.0
            return vec

    def index_document(self, doc_id: str, text: str, metadata: dict):
        """
        Inserts a fact check claim and evidence citation into the search index.
        """
        vector = self._get_embedding(text)
        payload = {
            "text": text,
            **metadata
        }
        
        if self.use_qdrant:
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        qmodels.PointStruct(
                            id=hash(doc_id) % (10**9), # numerical id
                            vector=vector,
                            payload=payload
                        )
                    ]
                )
            except Exception as e:
                logger.error(f"Qdrant indexing failed: {str(e)}")
        else:
            self.fallback_db.append({
                "id": doc_id,
                "text": text,
                "vector": vector,
                "payload": payload
            })

    def search_evidence(self, query: str, limit: int = 2) -> list:
        """
        Retrieves matching factcheck articles based on semantic search.
        """
        vector = self._get_embedding(query)
        
        if self.use_qdrant:
            try:
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=vector,
                    limit=limit
                )
                
                hits = []
                for res in results:
                    hits.append({
                        "text": res.payload.get("text"),
                        "source": res.payload.get("source", "Factcheck Library"),
                        "url": res.payload.get("url", "https://reeltruthchecker.com"),
                        "score": res.score
                    })
                return hits
            except Exception as e:
                logger.error(f"Qdrant query failed: {str(e)}")
                
        # In-memory cosine similarity fallback
        hits = []
        q_vec = np.array(vector)
        for doc in self.fallback_db:
            d_vec = np.array(doc["vector"])
            # Compute cosine similarity
            dot = np.dot(q_vec, d_vec)
            norm_q = np.linalg.norm(q_vec) or 1.0
            norm_d = np.linalg.norm(d_vec) or 1.0
            sim = float(dot / (norm_q * norm_d))
            
            # Substring bonus to boost keyword hits
            if query.lower() in doc["text"].lower() or any(w in doc["text"].lower() for w in query.lower().split() if len(w) > 4):
                sim += 0.2
                
            hits.append((sim, doc))
            
        hits.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "text": item[1]["text"],
                "source": item[1]["payload"].get("source"),
                "url": item[1]["payload"].get("url"),
                "score": item[0]
            }
            for item in hits[:limit]
        ]
