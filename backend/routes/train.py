from fastapi import APIRouter
from backend.schemas import StandardResponse, TrainRequest
from ml.trainer import train_pipeline
from ml.predictor import Predictor

router = APIRouter(tags=["Training"])


@router.post("/train", response_model=StandardResponse)
def train_model(req: TrainRequest):
    try:
        metadata = train_pipeline(
            data_path=req.file_path,
            target_col=req.target_column,
            text_cols=req.text_columns,
            task_type=req.task_type
        )
        return StandardResponse(success=True, data=metadata)
    except Exception as e:
        return StandardResponse(
            success=False,
            error={"code": "TRAINING_FAILED", "message": str(e)}
        )


@router.get("/training/status", response_model=StandardResponse)
def training_status():
    predictor = Predictor()
    return StandardResponse(
        success=True,
        data={
            "is_trained": predictor.is_ready,
            "metadata": predictor.metadata
        }
    )
