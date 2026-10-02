import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from .config import get_config
from .preprocessing import clean_text
from .utils import load_json


class Predictor:
    """Handles inference using trained artifacts saved in models/."""

    def __init__(self, models_dir: Optional[str] = None):
        config = get_config()
        self.models_dir = Path(models_dir or config.get("paths", {}).get("models_dir", "models"))
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.metadata = {}
        self.is_ready = False
        self._load_artifacts()

    def _load_artifacts(self):
        model_path = self.models_dir / "best_model.joblib"
        vec_path = self.models_dir / "vectorizer.joblib"
        meta_path = self.models_dir / "metadata.json"
        le_path = self.models_dir / "label_encoder.joblib"

        if model_path.exists() and vec_path.exists():
            try:
                self.model = joblib.load(model_path)
                self.vectorizer = joblib.load(vec_path)
                if le_path.exists():
                    self.label_encoder = joblib.load(le_path)
                if meta_path.exists():
                    self.metadata = load_json(meta_path)
                self.is_ready = True
            except Exception as e:
                print(f"[Warning] Failed to load model artifacts: {e}")
                self.is_ready = False

    def predict_single(self, text: str) -> Dict[str, Any]:
        if not self.is_ready or self.model is None or self.vectorizer is None:
            # Fallback mock prediction if model hasn't been trained yet
            return {
                "prediction": "General Candidate",
                "confidence": 0.50,
                "probabilities": {},
                "model_used": "Rule-Based Fallback",
                "status": "untrained"
            }

        cleaned = clean_text(text)
        X = self.vectorizer.transform(pd.Series([cleaned]))

        raw_pred = self.model.predict(X)[0]

        if self.label_encoder:
            pred_label = str(self.label_encoder.inverse_transform([raw_pred])[0])
        else:
            pred_label = str(raw_pred)

        probabilities = {}
        confidence = 1.0

        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X)[0]
            confidence = float(np.max(probs))
            classes = self.label_encoder.classes_ if self.label_encoder else range(len(probs))
            probabilities = {str(c): float(p) for c, p in zip(classes, probs)}
        elif hasattr(self.model, "decision_function"):
            decision = self.model.decision_function(X)[0]
            if isinstance(decision, np.ndarray):
                exp_d = np.exp(decision - np.max(decision))
                probs = exp_d / np.sum(exp_d)
                confidence = float(np.max(probs))
                classes = self.label_encoder.classes_ if self.label_encoder else range(len(probs))
                probabilities = {str(c): float(p) for c, p in zip(classes, probs)}

        return {
            "prediction": pred_label,
            "confidence": round(confidence, 4),
            "probabilities": probabilities,
            "model_used": self.metadata.get("model", "Saved Model"),
            "status": "success"
        }
