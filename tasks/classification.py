import pandas as pd
from typing import Dict, Any
from .base import BaseTask
from ml.trainer import train_pipeline
from ml.predictor import Predictor


class ClassificationTask(BaseTask):
    name = "classification"
    description = "Resume Job Role / Category Classification Task"

    def validate(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        target = config.get("dataset", {}).get("target")
        return target is not None and target in df.columns

    def execute(self, data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(data, dict) and "text" in data:
            predictor = Predictor()
            return predictor.predict_single(data["text"])
        else:
            # Training action
            return train_pipeline(task_type="classification")
