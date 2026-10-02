import numpy as np
from typing import List, Optional


class EmbeddingPipeline:
    """Embedding pipeline supporting optional sentence-transformers with fallback to TF-IDF vectorizer."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.is_available = False
        self._init_model()

    def _init_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.is_available = True
            print(f"[Info] SentenceTransformer '{self.model_name}' loaded successfully.")
        except Exception as e:
            self.is_available = False
            print(f"[Notice] SentenceTransformer unavailable ({e}). Fallback to TF-IDF feature engineering enabled.")

    def encode(self, texts: List[str]) -> Optional[np.ndarray]:
        if self.is_available and self.model is not None:
            try:
                return self.model.encode(texts, show_progress_bar=False)
            except Exception as e:
                print(f"[Warning] SentenceTransformer encoding failed: {e}. Falling back.")
                return None
        return None
