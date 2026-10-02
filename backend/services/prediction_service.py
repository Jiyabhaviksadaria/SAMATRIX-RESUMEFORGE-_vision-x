from typing import Dict, Any
from ml.predictor import Predictor
from ml.explainability import ModelExplainer
from ml.skill_extractor import extract_skills


def predict_and_explain(text: str) -> Dict[str, Any]:
    predictor = Predictor()
    pred_result = predictor.predict_single(text)

    # Generate explainability signals
    top_terms = []
    if predictor.vectorizer:
        top_terms = ModelExplainer.get_top_tfidf_features(predictor.vectorizer, text, top_n=8)

    skills_data = extract_skills(text)

    return {
        "prediction": pred_result["prediction"],
        "confidence": pred_result["confidence"],
        "probabilities": pred_result["probabilities"],
        "model_used": pred_result["model_used"],
        "status": pred_result["status"],
        "explanation": {
            "top_terms": top_terms,
            "detected_skills": skills_data["skills"][:8],
            "reasoning": f"Predicted '{pred_result['prediction']}' based on key signals in text."
        }
    }
