import time
import numpy as np
from typing import Dict, Any, List, Tuple
from .model_registry import ModelRegistry
from .evaluator import Evaluator


class ModelSelector:
    """Trains and compares multiple candidate models, selecting the best model based on task metrics."""

    def __init__(self, task_type: str = "classification", primary_metric: str = "f1", random_state: int = 42):
        self.task_type = task_type.lower()
        self.primary_metric = primary_metric.lower()
        self.random_state = random_state

    def compare_and_select(self, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> Tuple[Any, str, Dict[str, Any], List[Dict[str, Any]]]:
        leaderboard = []
        best_model = None
        best_model_name = ""
        best_metrics = {}
        best_score = -float("inf")

        if self.task_type == "regression":
            candidate_models = ModelRegistry.get_regression_models(self.random_state)
        else:
            candidate_models = ModelRegistry.get_classification_models(self.random_state)

        for name, model in candidate_models.items():
            # Fit model
            start_train = time.time()
            model.fit(X_train, y_train)
            train_time = time.time() - start_train

            # Predict
            start_pred = time.time()
            y_pred = model.predict(X_test)
            pred_time = time.time() - start_pred

            # Evaluate
            if self.task_type == "regression":
                metrics = Evaluator.evaluate_regression(y_test, y_pred)
                score = metrics.get(self.primary_metric, metrics["r2"])
            else:
                metrics = Evaluator.evaluate_classification(y_test, y_pred)
                score = metrics.get(self.primary_metric, metrics["f1"])

            model_info = {
                "name": name,
                "metrics": metrics,
                "train_time_sec": round(train_time, 4),
                "pred_time_sec": round(pred_time, 4),
                "primary_score": score
            }
            leaderboard.append(model_info)

            if score > best_score:
                best_score = score
                best_model = model
                best_model_name = name
                best_metrics = metrics

        # Sort leaderboard descending by primary score
        leaderboard.sort(key=lambda x: x["primary_score"], reverse=True)

        return best_model, best_model_name, best_metrics, leaderboard
