from fastapi import APIRouter
from backend.schemas import StandardResponse, PredictRequest
from backend.services.prediction_service import predict_and_explain

router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=StandardResponse)
def predict_endpoint(req: PredictRequest):
    try:
        res = predict_and_explain(req.text)
        return StandardResponse(success=True, data=res)
    except Exception as e:
        return StandardResponse(
            success=False,
            error={"code": "PREDICTION_FAILED", "message": str(e)}
        )
