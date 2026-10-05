from typing import Dict, Any
from ml.training.predict_resume import predict_resume
from ml.skill_extractor import extract_skills


def predict_and_explain(text: str) -> Dict[str, Any]:
    pred_result = predict_resume(text)

    skills_data = extract_skills(text)

    return {
        "prediction": pred_result["category"],
        "confidence": pred_result["confidence"],
        "probabilities": {p["category"]: p["confidence"] for p in pred_result["top_predictions"]},
        "model_used": "Linear SVM (Word+Char TF-IDF)",
        "status": "success",
        "explanation": {
            "top_terms": [],
            "detected_skills": skills_data["skills"][:8],
            "reasoning": f"Predicted '{pred_result['category']}' based on key signals in text."
        }
    }
