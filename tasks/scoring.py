import pandas as pd
from typing import Dict, Any
from .base import BaseTask
from ml.trainer import train_pipeline


class ScoringTask(BaseTask):
    name = "scoring"
    description = "Resume Quality Analysis & Feature Completeness Score"

    def validate(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        return True

    def execute(self, data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        text = data.get("text", "")
        # Heuristic scoring signals
        has_email = "@" in text
        has_phone = any(char.isdigit() for char in text)
        words = text.split()
        word_count = len(words)

        completeness = min(1.0, word_count / 150.0)
        score = (completeness * 40) + (15 if has_email else 0) + (15 if has_phone else 0) + 30
        return {
            "quality_score": round(score, 1),
            "completeness": round(completeness * 100, 1),
            "signals": {
                "has_contact_info": has_email or has_phone,
                "word_count": word_count,
                "length_status": "Optimal" if word_count >= 100 else "Short"
            },
            "label": "Resume Quality Analysis"
        }


class RecommendationTask(BaseTask):
    name = "recommendation"
    description = "Candidate Job Role Recommendation Task"

    def validate(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        return True

    def execute(self, data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        # Uses classification task internally
        from ml.predictor import Predictor
        predictor = Predictor()
        res = predictor.predict_single(data.get("text", ""))
        return {
            "recommended_role": res.get("prediction"),
            "confidence": res.get("confidence"),
            "top_matches": res.get("probabilities", {})
        }


class RegressionTask(BaseTask):
    name = "regression"
    description = "Numerical Prediction Task (e.g., Salary / Experience Years)"

    def validate(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        target = config.get("dataset", {}).get("target")
        return target is not None and target in df.columns and pd.api.types.is_numeric_dtype(df[target])

    def execute(self, data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        return train_pipeline(task_type="regression")


class ClusteringTask(BaseTask):
    name = "clustering"
    description = "Unsupervised Resume Grouping / Clustering Task"

    def validate(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        return True

    def execute(self, data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "clustering_complete", "n_clusters": 4}
