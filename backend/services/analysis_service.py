import re
from typing import Dict, Any, List
from ml.skill_extractor import extract_skills
from ml.preprocessing import clean_text


def parse_and_analyze_resume(text: str, candidate_name: str = "Anonymous Candidate") -> Dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        text = ""

    # Extract email & phone
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    email = email_match.group(0) if email_match else "Not detected"

    phone_match = re.search(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}', text)
    phone = phone_match.group(0) if phone_match else "Not detected"

    # Extract skills
    skills_data = extract_skills(text)

    # Heuristic section detection
    text_lower = text.lower()
    has_education = any(w in text_lower for w in ["education", "bachelor", "master", "phd", "degree", "university", "college", "bs", "ms"])
    has_experience = any(w in text_lower for w in ["experience", "employment", "history", "work", "role", "engineer", "developer", "manager"])
    has_projects = any(w in text_lower for w in ["project", "portfolio", "built", "developed"])
    has_certifications = any(w in text_lower for w in ["certification", "certified", "license", "aws", "azure", "certificate"])

    # Education degree detection
    education_level = "Not Specified"
    if "phd" in text_lower or "doctorate" in text_lower:
        education_level = "PhD / Doctorate"
    elif "master" in text_lower or "ms" in text_lower or "m.s." in text_lower or "mba" in text_lower:
        education_level = "Master's Degree"
    elif "bachelor" in text_lower or "bs" in text_lower or "b.s." in text_lower or "b.tech" in text_lower:
        education_level = "Bachelor's Degree"

    # Calculate Quality Score
    word_count = len(text.split())
    length_score = min(30, (word_count / 150.0) * 30)
    contact_score = (15 if email != "Not detected" else 0) + (15 if phone != "Not detected" else 0)
    skill_score = min(20, skills_data["total_count"] * 4)
    section_score = (5 if has_education else 0) + (5 if has_experience else 0) + (5 if has_projects else 0) + (5 if has_certifications else 0)

    quality_score = round(length_score + contact_score + skill_score + section_score, 1)

    return {
        "candidate": {
            "name": candidate_name,
            "email": email,
            "phone": phone,
            "detected_education_level": education_level
        },
        "skills": skills_data,
        "section_detection": {
            "education": has_education,
            "experience": has_experience,
            "projects": has_projects,
            "certifications": has_certifications
        },
        "quality_analysis": {
            "overall_score": quality_score,
            "label": "Resume Quality Analysis",
            "word_count": word_count,
            "breakdown": {
                "length_score": round(length_score, 1),
                "contact_score": contact_score,
                "skill_score": skill_score,
                "section_score": section_score
            }
        },
        "text_summary": text[:300] + "..." if len(text) > 300 else text
    }
