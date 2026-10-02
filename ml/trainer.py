import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from .config import get_config
from .data_loader import load_dataset
from .data_profiler import profile_dataset
from .preprocessing import prepare_text_dataset
from .feature_engineering import FeaturePipeline
from .model_selector import ModelSelector
from .utils import save_json


def train_pipeline(data_path: Optional[str] = None,
                   target_col: Optional[str] = None,
                   text_cols: Optional[List[str]] = None,
                   task_type: Optional[str] = None) -> Dict[str, Any]:
    config = get_config()
    d_path = data_path or config["dataset"]["path"]
    t_col = target_col or config["dataset"]["target"]
    txt_cols = text_cols or config["text"]["columns"]
    t_type = task_type or config["task"]["type"]

    # Load dataset
    df = load_dataset(d_path)
    profiler = profile_dataset(df, t_col)

    if not t_col or t_col not in df.columns:
        t_col = profiler.get("selected_target")
        if not t_col:
            raise ValueError("No target column specified and unable to infer target automatically.")

    if not txt_cols:
        txt_cols = profiler.get("text_columns", [])
        if not txt_cols:
            # Fallback to any text/object columns except target
            txt_cols = [c for c in df.columns if c != t_col and df[c].dtype == 'object']

    if t_type == "auto" or not t_type:
        t_type = profiler.get("recommended_task", "classification")

    # Drop missing target values
    df = df.dropna(subset=[t_col]).reset_index(drop=True)
    if len(df) < 5:
        raise ValueError(f"Insufficient data rows ({len(df)}) after dropping missing target values.")

    # Prepare text features
    raw_text, clean_text = prepare_text_dataset(df, txt_cols)

    # Fit TF-IDF Feature Pipeline
    tfidf_config = config.get("features", {}).get("tfidf", {})
    pipeline = FeaturePipeline(
        max_features=tfidf_config.get("max_features", 10000),
        ngram_range=tfidf_config.get("ngram_range", [1, 2])
    )
    X = pipeline.fit_transform(clean_text)

    # Encode target if classification
    label_encoder = None
    y = df[t_col].values
    if t_type != "regression" and (isinstance(y[0], str) or pd.api.types.is_object_dtype(df[t_col])):
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(df[t_col].astype(str))

    # Split dataset
    test_size = config.get("training", {}).get("test_size", 0.2)
    random_state = config.get("model", {}).get("random_state", 42)

    min_class_count = pd.Series(y).value_counts().min() if t_type != "regression" else 0
    stratify = y if (t_type != "regression" and len(np.unique(y)) > 1 and min_class_count >= 2) else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )

    # Run Model Selector
    selector = ModelSelector(
        task_type=t_type,
        primary_metric=config.get("model", {}).get("metric", "f1"),
        random_state=random_state
    )
    best_model, best_name, best_metrics, leaderboard = selector.compare_and_select(X_train, y_train, X_test, y_test)

    # Save artifacts
    models_dir = Path(config.get("paths", {}).get("models_dir", "models"))
    os.makedirs(models_dir, exist_ok=True)

    joblib.dump(best_model, models_dir / "best_model.joblib")
    joblib.dump(pipeline, models_dir / "vectorizer.joblib")
    if label_encoder:
        joblib.dump(label_encoder, models_dir / "label_encoder.joblib")

    metadata = {
        "task": t_type,
        "target": t_col,
        "text_columns": txt_cols,
        "model": best_name,
        "metrics": best_metrics,
        "leaderboard": leaderboard,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "trained_at": datetime.now().isoformat(),
        "classes": label_encoder.classes_.tolist() if label_encoder else None
    }
    save_json(metadata, models_dir / "metadata.json")

    return metadata
