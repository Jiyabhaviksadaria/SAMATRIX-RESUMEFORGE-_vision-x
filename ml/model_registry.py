from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.cluster import KMeans
from typing import Dict, Any, List


class ModelRegistry:
    """Registry providing lightweight ML models for classification, regression, and clustering."""

    @staticmethod
    def get_classification_models(random_state: int = 42) -> Dict[str, Any]:
        models = {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=random_state, class_weight="balanced"),
            "Linear SVM": LinearSVC(random_state=random_state, class_weight="balanced", dual="auto"),
            "Random Forest": RandomForestClassifier(n_estimators=100, random_state=random_state, class_weight="balanced"),
            "Gradient Boosting": GradientBoostingClassifier(n_estimators=50, random_state=random_state)
        }
        # Optional XGBoost import with fallback
        try:
            from xgboost import XGBClassifier
            models["XGBoost"] = XGBClassifier(n_estimators=50, random_state=random_state, eval_metric="logloss")
        except ImportError:
            pass
        return models

    @staticmethod
    def get_regression_models(random_state: int = 42) -> Dict[str, Any]:
        return {
            "Linear Regression": LinearRegression(),
            "Random Forest Regressor": RandomForestRegressor(n_estimators=100, random_state=random_state),
            "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=50, random_state=random_state)
        }

    @staticmethod
    def get_clustering_models(n_clusters: int = 4, random_state: int = 42) -> Dict[str, Any]:
        return {
            "KMeans": KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        }
