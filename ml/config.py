import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

_GLOBAL_CONFIG: Optional[Dict[str, Any]] = None

DEFAULT_CONFIG = {
    "task": {"type": "auto"},
    "dataset": {
        "path": "data/sample/sample_resumes.csv",
        "target": None
    },
    "text": {"columns": []},
    "features": {
        "tfidf": {
            "enabled": True,
            "max_features": 10000,
            "ngram_range": [1, 2],
            "min_df": 1,
            "max_df": 1.0
        }
    },
    "model": {
        "strategy": "auto",
        "metric": "f1",
        "random_state": 42
    },
    "training": {
        "test_size": 0.2,
        "cv_folds": 3
    },
    "advanced": {
        "embeddings": False,
        "xgboost": False,
        "llm": False
    },
    "paths": {
        "models_dir": "models",
        "outputs_dir": "outputs",
        "data_dir": "data"
    }
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    global _GLOBAL_CONFIG
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f) or {}
                # Deep merge defaults
                config = _deep_merge(DEFAULT_CONFIG, loaded)
                _GLOBAL_CONFIG = config
                return config
        except Exception as e:
            print(f"[Warning] Failed to parse config file at {path}: {e}. Using defaults.")
    _GLOBAL_CONFIG = DEFAULT_CONFIG.copy()
    return _GLOBAL_CONFIG


def get_config() -> Dict[str, Any]:
    global _GLOBAL_CONFIG
    if _GLOBAL_CONFIG is None:
        return load_config()
    return _GLOBAL_CONFIG


def update_config(updates: Dict[str, Any], config_path: Optional[str] = None) -> Dict[str, Any]:
    global _GLOBAL_CONFIG
    current = get_config()
    updated = _deep_merge(current, updates)
    _GLOBAL_CONFIG = updated
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    try:
        os.makedirs(path.parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(updated, f, default_flow_style=False)
    except Exception as e:
        print(f"[Warning] Failed to save updated config to {path}: {e}")
    return _GLOBAL_CONFIG


def _deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
