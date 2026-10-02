import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.schemas import StandardResponse, AnalyzeResumeRequest, SkillExtractRequest
from backend.services.analysis_service import parse_and_analyze_resume
from backend.services.file_service import extract_text_from_file
from ml.skill_extractor import extract_skills

router = APIRouter(tags=["Analysis"])


@router.post("/analyze-resume", response_model=StandardResponse)
async def analyze_resume_endpoint(
    text: str = Form(None),
    candidate_name: str = Form("Anonymous Candidate"),
    file: UploadFile = File(None)
):
    resume_content = ""
    if file and file.filename:
        # Save temp file
        temp_dir = Path("data/raw/temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        file_path = temp_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        resume_content = extract_text_from_file(str(file_path))
    elif text:
        resume_content = text
    else:
        raise HTTPException(status_code=400, detail="Provide either text content or an uploaded file.")

    analysis = parse_and_analyze_resume(resume_content, candidate_name)
    return StandardResponse(success=True, data=analysis)


@router.post("/extract-skills", response_model=StandardResponse)
def extract_skills_endpoint(req: SkillExtractRequest):
    data = extract_skills(req.text)
    return StandardResponse(success=True, data=data)
