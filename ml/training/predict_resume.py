"""
Member 2 prediction contract for Member 3.

Usage:
    from ml.training.predict_resume import predict_resume
    result = predict_resume("resume text here")
"""

from pathlib import Path
import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models"


def _load():
    model = joblib.load(MODEL_DIR / "best_model.joblib")
    vectorizer = joblib.load(MODEL_DIR / "vectorizer.joblib")
    encoder = joblib.load(MODEL_DIR / "label_encoder.joblib")
    return model, vectorizer, encoder


def predict_resume(text: str, top_k: int = 3):
    model, vectorizer, encoder = _load()
    X = vectorizer.transform([text])

    predicted_id = model.predict(X)[0]
    predicted = encoder.inverse_transform([predicted_id])[0]

    # LinearSVC has decision_function but no predict_proba.
    scores = model.decision_function(X)[0]
    scores = np.asarray(scores)

    if scores.ndim == 0:
        scores = np.array([float(scores)])

    # Convert decision scores to a relative softmax-like confidence for UI only.
    shifted = scores - np.max(scores)
    exp_scores = np.exp(shifted)
    probabilities = exp_scores / exp_scores.sum()

    order = np.argsort(probabilities)[::-1][:top_k]
    top_predictions = [
        {
            "category": str(encoder.inverse_transform([i])[0]),
            "confidence": round(float(probabilities[i]), 4),
        }
        for i in order
    ]

    return {
        "category": str(predicted),
        "confidence": round(float(probabilities[predicted_id]), 4),
        "top_predictions": top_predictions,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    args = parser.parse_args()
    print(predict_resume(args.text))
