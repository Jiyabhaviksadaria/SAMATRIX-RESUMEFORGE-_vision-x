import os
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.schemas import StandardResponse, ProfileRequest
from ml.data_loader import load_dataset
from ml.data_profiler import profile_dataset
from ml.config import get_config, update_config

router = APIRouter(prefix="/dataset", tags=["Dataset"])


@router.post("/upload", response_model=StandardResponse)
async def upload_dataset(file: UploadFile = File(...)):
    filename = file.filename or "uploaded_dataset.csv"
    ext = Path(filename).suffix.lower()

    if ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(status_code=400, detail="Invalid file extension. Allowed: .csv, .xlsx, .xls")

    target_dir = Path(get_config()["paths"]["data_dir"]) / "raw"
    os.makedirs(target_dir, exist_ok=True)
    save_path = target_dir / filename

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

    # Update config with new dataset path
    update_config({"dataset": {"path": str(save_path)}})

    # Automatically profile uploaded dataset
    df = load_dataset(str(save_path))
    profile = profile_dataset(df)

    return StandardResponse(
        success=True,
        data={
            "filename": filename,
            "saved_path": str(save_path),
            "profile": profile
        }
    )


@router.post("/profile", response_model=StandardResponse)
def profile_endpoint(req: ProfileRequest):
    config = get_config()
    file_path = req.file_path or config["dataset"]["path"]
    target_col = req.target_column or config["dataset"]["target"]

    try:
        df = load_dataset(file_path)
        profile = profile_dataset(df, target_col)
        return StandardResponse(success=True, data=profile)
    except Exception as e:
        return StandardResponse(
            success=False,
            error={"code": "PROFILING_FAILED", "message": str(e)}
        )
