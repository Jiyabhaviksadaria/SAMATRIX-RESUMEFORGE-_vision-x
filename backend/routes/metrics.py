from fastapi import APIRouter
from backend.schemas import StandardResponse
from ml.predictor import Predictor
from ml.explainability import ModelExplainer

router = APIRouter(tags=["Metrics & Models"])


@router.get("/metrics", response_model=StandardResponse)
def get_metrics():
    predictor = Predictor()
    if not predictor.is_ready:
        return StandardResponse(
            success=True,
            data={
                "status": "untrained",
                "message": "No model trained yet. Run /train first."
            }
        )

    # Feature importance
    feature_importance = []
    if predictor.model and predictor.vectorizer:
        feature_importance = ModelExplainer.explain_model_importance(predictor.model, predictor.vectorizer)

    return StandardResponse(
        success=True,
        data={
            "status": "trained",
            "model_name": predictor.metadata.get("model"),
            "metrics": predictor.metadata.get("metrics"),
            "leaderboard": predictor.metadata.get("leaderboard", []),
            "train_rows": predictor.metadata.get("train_rows"),
            "test_rows": predictor.metadata.get("test_rows"),
            "trained_at": predictor.metadata.get("trained_at"),
            "feature_importance": feature_importance
        }
    )


@router.get("/model/info", response_model=StandardResponse)
def get_model_info():
    predictor = Predictor()
    return StandardResponse(
        success=True,
        data={
            "is_ready": predictor.is_ready,
            "metadata": predictor.metadata
        }
    )
