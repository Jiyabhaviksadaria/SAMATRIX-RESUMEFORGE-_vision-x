import os
import json
import time
import numpy as np
from pathlib import Path
from typing import Any, Dict


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types and Path objects."""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


def save_json(data: Dict[str, Any], file_path: str) -> None:
    path = Path(file_path)
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, cls=JSONEncoder)


def load_json(file_path: str) -> Dict[str, Any]:
    path = Path(file_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class Timer:
    """Utility timer context manager for timing code execution."""
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.duration = self.end - self.start
