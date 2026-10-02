from typing import Dict, Any, List
from .similarity import calculate_job_matching


def rank_candidates(candidates: List[Dict[str, Any]], job_description: str) -> List[Dict[str, Any]]:
    """Ranks multiple candidates against a job description in an explainable order."""
    ranked_results = []

    for idx, cand in enumerate(candidates):
        cand_id = cand.get("candidate_id", f"cand_{idx+1}")
        cand_name = cand.get("candidate_name", f"Candidate {idx+1}")
        resume_text = cand.get("resume_text", "")

        match_info = calculate_job_matching(resume_text, job_description)

        ranked_results.append({
            "candidate_id": cand_id,
            "candidate_name": cand_name,
            "similarity_score": match_info["similarity_score"],
            "similarity_percentage": match_info["similarity_percentage"],
            "matching_skills": match_info["matching_skills"],
            "missing_skills": match_info["missing_skills"],
            "skill_count": len(match_info["matching_skills"]),
            "method": match_info["method"]
        })

    # Sort descending by similarity score
    ranked_results.sort(key=lambda x: x["similarity_score"], reverse=True)

    # Assign rank numbers
    for rank_idx, item in enumerate(ranked_results):
        item["rank"] = rank_idx + 1

    return ranked_results
