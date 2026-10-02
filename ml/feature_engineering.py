import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from typing import Dict, Any, List, Optional, Tuple


class FeaturePipeline:
    """Feature engineering pipeline managing TF-IDF vectorization and structured column transformers."""

    def __init__(self,
                 max_features: int = 10000,
                 ngram_range: Tuple[int, int] = (1, 2),
                 min_df: int = 1,
                 max_df: float = 1.0):
        self.max_features = max_features
        self.ngram_range = tuple(ngram_range)
        self.min_df = min_df
        self.max_df = max_df
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.is_fitted = False

    def fit_transform(self, text_series: pd.Series) -> np.ndarray:
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            max_df=self.max_df,
            sublinear_tf=True
        )
        X = self.vectorizer.fit_transform(text_series.fillna("")).toarray()
        self.is_fitted = True
        return X

    def transform(self, text_series: pd.Series) -> np.ndarray:
        if not self.is_fitted or self.vectorizer is None:
            raise ValueError("FeaturePipeline is not fitted yet. Call fit_transform first.")
        return self.vectorizer.transform(text_series.fillna("")).toarray()

    def get_feature_names(self) -> List[str]:
        if self.vectorizer and hasattr(self.vectorizer, "get_feature_names_out"):
            return list(self.vectorizer.get_feature_names_out())
        return []
