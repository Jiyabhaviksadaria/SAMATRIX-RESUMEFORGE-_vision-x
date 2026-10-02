from fastapi import APIRouter
from backend.schemas import StandardResponse, MatchRequest, RankRequest
from ml.similarity import calculate_job_matching
from ml.ranking import rank_candidates

router = APIRouter(tags=["Matching & Ranking"])


@router.post("/match", response_model=StandardResponse)
def match_endpoint(req: MatchRequest):
    res = calculate_job_matching(
        resume_text=req.resume_text,
        job_description=req.job_description,
        use_embeddings=req.use_embeddings
    )
    return StandardResponse(success=True, data=res)


@router.post("/rank", response_model=StandardResponse)
def rank_endpoint(req: RankRequest):
    candidates_list = [c.model_dump() for c in req.candidates]
    rankings = rank_candidates(candidates_list, req.job_description)
    return StandardResponse(
        success=True,
        data={
            "rankings": rankings,
            "total_candidates": len(rankings)
        }
    )
