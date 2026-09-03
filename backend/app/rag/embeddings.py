import numpy as np
from typing import List, Optional
from app.core.config import settings
from app.core.logging import logger

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class EmbeddingService:
    """Service to generate dense vector embeddings for texts using Google text-embedding-004."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GOOGLE_EMBEDDING_MODEL
        self.dimension = 768
        self.client = None

        if self.api_key and GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized EmbeddingService with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize GenAI Embedding Client: {e}")
                self.client = None

    async def get_embedding(self, text: str) -> List[float]:
        """Generate a single 768-dim embedding for a text."""
        embeddings = await self.get_batch_embeddings([text])
        return embeddings[0] if embeddings else self._generate_pseudo_embedding(text)

    async def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts in batches."""
        if not texts:
            return []

        if not self.client:
            logger.info("Using pseudo-embeddings for local/dev/test mode.")
            return [self._generate_pseudo_embedding(t) for t in texts]

        results = []
        # Batch by 50 texts per call
        batch_size = 50
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                # Truncate texts to 2048 chars to avoid token limits
                cleaned_batch = [t[:2048] for t in batch]
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=cleaned_batch,
                )
                if hasattr(response, "embeddings") and response.embeddings:
                    for emb in response.embeddings:
                        results.append(emb.values)
                else:
                    results.extend([self._generate_pseudo_embedding(t) for t in batch])
            except Exception as e:
                logger.error(f"Batch embedding generation failed: {e}")
                results.extend([self._generate_pseudo_embedding(t) for t in batch])

        return results

    def _generate_pseudo_embedding(self, text: str) -> List[float]:
        """Deterministic pseudo-embedding for testing or offline environments."""
        # Use hash-based pseudo random vector of dimension 768 normalized to unit length
        seed = abs(hash(text)) % (2**32)
        rng = np.random.RandomState(seed)
        vec = rng.randn(self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()


embedding_service = EmbeddingService()
