import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, Any, List, Optional
from .preprocessing import clean_text
from .skill_extractor import extract_skills
from .embeddings import EmbeddingPipeline


def calculate_job_matching(resume_text: str, job_description: str, use_embeddings: bool = False) -> Dict[str, Any]:
    if not resume_text.strip() or not job_description.strip():
        return {
            "similarity_score": 0.0,
            "similarity_percentage": "0.0%",
            "matching_skills": [],
            "missing_skills": [],
            "method": "TF-IDF + Cosine Similarity",
            "breakdown": {}
        }

    clean_resume = clean_text(resume_text)
    clean_job = clean_text(job_description)

    # Extract skills from both text inputs
    resume_skills_data = extract_skills(resume_text)
    job_skills_data = extract_skills(job_description)

    resume_skills = set(resume_skills_data["skills"])
    job_skills = set(job_skills_data["skills"])

    matching_skills = sorted(list(resume_skills.intersection(job_skills)))
    missing_skills = sorted(list(job_skills.difference(resume_skills)))

    # Compute cosine similarity
    score = 0.0
    method = "TF-IDF + Cosine Similarity"

    if use_embeddings:
        pipe = EmbeddingPipeline()
        encoded = pipe.encode([clean_resume, clean_job])
        if encoded is not None and len(encoded) == 2:
            score = float(cosine_similarity([encoded[0]], [encoded[1]])[0][0])
            method = "SentenceTransformer + Cosine Similarity"
        else:
            # Fallback to TF-IDF
            vec = TfidfVectorizer(ngram_range=(1, 2)).fit([clean_resume, clean_job])
            vectors = vec.transform([clean_resume, clean_job]).toarray()
            score = float(cosine_similarity([vectors[0]], [vectors[1]])[0][0])
    else:
        vec = TfidfVectorizer(ngram_range=(1, 2)).fit([clean_resume, clean_job])
        vectors = vec.transform([clean_resume, clean_job]).toarray()
        score = float(cosine_similarity([vectors[0]], [vectors[1]])[0][0])

    # Bound similarity score between 0.0 and 1.0
    score = max(0.0, min(1.0, score))
    pct = f"{round(score * 100, 1)}%"

    skill_overlap_ratio = len(matching_skills) / max(1, len(job_skills)) if job_skills else 1.0

    return {
        "similarity_score": round(score, 4),
        "similarity_percentage": pct,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "skill_overlap_ratio": round(skill_overlap_ratio, 4),
        "method": method,
        "label": "Profile-to-Job Similarity",
        "breakdown": {
            "text_similarity": round(score, 4),
            "matching_skills_count": len(matching_skills),
            "missing_skills_count": len(missing_skills),
            "total_job_skills_detected": len(job_skills)
        }
    }
