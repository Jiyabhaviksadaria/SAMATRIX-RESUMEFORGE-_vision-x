import tempfile
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, Form, HTTPException

from backend.schemas import StandardResponse
from scripts.data.extract_resumes import extract_pdf_text
from ml.training.predict_resume import predict_resume

router = APIRouter(tags=["Resume Classification"])

MAX_SIZE_BYTES = 10 * 1024 * 1024


def _classify(text: str, filename: str) -> dict:
    if not text or not text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable resume text was found.",
        )
    result = predict_resume(text, top_k=5)
    return {
        "filename": filename,
        "predicted_category": result["category"],
        "confidence": result["confidence"],
        "top_predictions": result["top_predictions"],
        "extracted_text_length": len(text),
        "model": "Linear SVM (Word TF-IDF + Character TF-IDF)",
    }


@router.post("/classify", response_model=StandardResponse)
async def classify_resume(
    file: UploadFile = File(None),
    text: str = Form(None),
):
    if file is not None and file.filename:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Please upload a valid PDF.")
        content = await file.read()
        if len(content) > MAX_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="File too large. Maximum recommended size: 10 MB.")
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(content)
        tmp.close()
        try:
            text_extracted = extract_pdf_text(Path(tmp.name))
        except Exception:
            raise HTTPException(status_code=422, detail="We couldn't extract readable text from this resume.")
        finally:
            Path(tmp.name).unlink(missing_ok=True)
        data = _classify(text_extracted, file.filename)
        return StandardResponse(success=True, data=data)

    if text and text.strip():
        data = _classify(text.strip(), "demo_text_input")
        return StandardResponse(success=True, data=data)

    raise HTTPException(status_code=400, detail="Provide a PDF file or resume text.")
