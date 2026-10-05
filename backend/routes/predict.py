from fastapi import APIRouter, HTTPException
from backend.schemas import StandardResponse, PredictRequest
from backend.services.prediction_service import predict_and_explain

router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=StandardResponse)
def predict_endpoint(req: PredictRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(
            status_code=400,
            detail=StandardResponse(
                success=False,
                error={"code": "INVALID_INPUT", "message": "Resume text cannot be empty"}
            ).model_dump()
        )
    try:
        res = predict_and_explain(req.text)
        return StandardResponse(success=True, data=res)
    except Exception as e:
        return StandardResponse(
            success=False,
            error={"code": "PREDICTION_FAILED", "message": str(e)}
        )
