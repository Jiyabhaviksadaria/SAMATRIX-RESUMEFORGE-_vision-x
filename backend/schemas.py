from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class StandardResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class ProfileRequest(BaseModel):
    file_path: Optional[str] = None
    target_column: Optional[str] = None


class TrainRequest(BaseModel):
    file_path: Optional[str] = None
    target_column: Optional[str] = None
    text_columns: Optional[List[str]] = None
    task_type: Optional[str] = None


class PredictRequest(BaseModel):
    text: str = Field(..., description="Resume text to predict job role/category for")


class AnalyzeResumeRequest(BaseModel):
    text: Optional[str] = None
    candidate_name: Optional[str] = "Anonymous Candidate"


class SkillExtractRequest(BaseModel):
    text: str


class MatchRequest(BaseModel):
    resume_text: str
    job_description: str
    use_embeddings: bool = False


class CandidateItem(BaseModel):
    candidate_id: str
    candidate_name: str
    resume_text: str


class RankRequest(BaseModel):
    candidates: List[CandidateItem]
    job_description: str


class ConfigUpdateRequest(BaseModel):
    task: Optional[Dict[str, Any]] = None
    dataset: Optional[Dict[str, Any]] = None
    text: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any]] = None
    model: Optional[Dict[str, Any]] = None
