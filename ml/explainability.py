import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from .preprocessing import clean_text


class ModelExplainer:
    """Provides model explainability: feature importances, top TF-IDF N-grams, and signal analysis."""

    @staticmethod
    def get_top_tfidf_features(vectorizer, text: str, top_n: int = 10) -> List[Dict[str, Any]]:
        if not vectorizer or not hasattr(vectorizer, "get_feature_names"):
            return []

        cleaned = clean_text(text)
        feature_names = vectorizer.get_feature_names()
        X = vectorizer.transform(pd.Series([cleaned]))[0]

        if not len(feature_names) or not len(X):
            return []

        indices = np.argsort(X)[::-1][:top_n]
        top_features = []
        for idx in indices:
            score = float(X[idx])
            if score > 0:
                top_features.append({
                    "term": feature_names[idx],
                    "weight": round(score, 4)
                })
        return top_features

    @staticmethod
    def explain_model_importance(model, vectorizer, top_n: int = 15) -> List[Dict[str, Any]]:
        if not model or not vectorizer or not hasattr(vectorizer, "get_feature_names"):
            return []

        feature_names = vectorizer.get_feature_names()

        # Tree-based model feature importances
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:top_n]
            return [
                {"feature": feature_names[i], "importance": round(float(importances[i]), 4)}
                for i in indices
            ]
        # Linear model coefficients
        elif hasattr(model, "coef_"):
            coef = model.coef_
            if coef.ndim > 1:
                coef = np.mean(np.abs(coef), axis=0)
            else:
                coef = np.abs(coef)
            indices = np.argsort(coef)[::-1][:top_n]
            return [
                {"feature": feature_names[i], "importance": round(float(coef[i]), 4)}
                for i in indices
            ]

        return []
