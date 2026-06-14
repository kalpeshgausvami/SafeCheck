import numpy as np
from sklearn.cluster import DBSCAN
from backend.app.intelligence.config import DBSCAN_EPS, DBSCAN_MIN_SAMPLES
import logging

logger = logging.getLogger(__name__)

class ClaimClusteringEngine:
    """
    Groups posts containing similar assertions using sentence embedding distance and DBSCAN.
    """
    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            self.has_embedder = True
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer in clustering engine: {str(e)}. Using keyword overlap clustering.")
            self.has_embedder = False

    def cluster_posts(self, posts: list) -> list:
        """
        Groups similar text fields and returns cluster ID mapping.
        """
        if not posts:
            return []

        texts = [p.get("text", "") for p in posts]

        if not self.has_embedder:
            return self._keyword_cluster(posts)

        try:
            embeddings = self.embedder.encode(texts)
            
            # Run DBSCAN
            db = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES, metric="cosine").fit(embeddings)
            labels = db.labels_
            
            clustered_posts = []
            for idx, p in enumerate(posts):
                c_id = int(labels[idx])
                # Convert noise labels (-1) to individual singletons
                if c_id == -1:
                    c_id = 1000 + idx
                
                clustered_posts.append({
                    **p,
                    "cluster_id": c_id
                })
            return clustered_posts
        except Exception as e:
            logger.error(f"DBSCAN clustering failed: {str(e)}. Using fallback.")
            return self._keyword_cluster(posts)

    def _keyword_cluster(self, posts: list) -> list:
        """
        Lexical overlap based clustering fallback.
        """
        clustered_posts = []
        # Group posts sharing core words
        core_topics = [
            ("lemon", 101),
            ("solar", 102),
            ("bank", 103),
            ("vaccine", 104),
            ("election", 105),
            ("drought", 106)
        ]
        
        for idx, p in enumerate(posts):
            text_lower = p.get("text", "").lower()
            assigned_cluster = 1000 + idx # default singleton
            
            for word, c_id in core_topics:
                if word in text_lower:
                    assigned_cluster = c_id
                    break
                    
            clustered_posts.append({
                **p,
                "cluster_id": assigned_cluster
            })
            
        return clustered_posts
