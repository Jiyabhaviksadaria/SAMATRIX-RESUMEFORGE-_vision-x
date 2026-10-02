from fastapi import APIRouter
from backend.schemas import StandardResponse
from ml.trainer import train_pipeline
from ml.predictor import Predictor
from ml.config import update_config, get_config

router = APIRouter(tags=["Demo"])


@router.post("/demo/load", response_model=StandardResponse)
def load_demo_data():
    sample_dataset_path = "data/sample/sample_resumes.csv"

    # Update config for demo dataset
    update_config({
        "dataset": {
            "path": sample_dataset_path,
            "target": "job_role"
        },
        "text": {
            "columns": ["resume_text"]
        },
        "task": {
            "type": "classification"
        }
    })

    # Train pipeline on demo data
    try:
        metadata = train_pipeline(
            data_path=sample_dataset_path,
            target_col="job_role",
            text_cols=["resume_text"],
            task_type="classification"
        )
        return StandardResponse(
            success=True,
            data={
                "message": "Demo data loaded and baseline model successfully trained.",
                "dataset_path": sample_dataset_path,
                "metadata": metadata
            }
        )
    except Exception as e:
        return StandardResponse(
            success=False,
            error={"code": "DEMO_LOAD_FAILED", "message": str(e)}
        )
