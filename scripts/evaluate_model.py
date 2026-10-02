import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.predictor import Predictor
from ml.explainability import ModelExplainer


def main():
    print(f"\n==========================================")
    print(f" RESUMEFORGE AI — MODEL EVALUATION REPORT")
    print(f"==========================================")

    predictor = Predictor()
    if not predictor.is_ready:
        print("❌ No trained model artifacts found. Please run scripts/train_model.py first.")
        sys.exit(1)

    meta = predictor.metadata
    print(f"✓ Model: {meta.get('model')}")
    print(f"✓ Target Column: {meta.get('target')}")
    print(f"✓ Task Type: {meta.get('task')}")
    print(f"✓ Trained At: {meta.get('trained_at')}")

    print("\nPerformance Metrics:")
    for k, v in meta.get("metrics", {}).items():
        if isinstance(v, (int, float)):
            print(f"   - {k.upper():<15}: {v}")

    print("\nLeaderboard Comparison:")
    for idx, item in enumerate(meta.get("leaderboard", [])):
        print(f"   #{idx+1} {item['name']:<25} | Score: {item['primary_score']:.4f}")

    if predictor.model and predictor.vectorizer:
        print("\nTop Global Feature Importances:")
        features = ModelExplainer.explain_model_importance(predictor.model, predictor.vectorizer, top_n=10)
        for f in features:
            print(f"   - {f['feature']:<20} Weight: {f['importance']}")

    print(f"==========================================")


if __name__ == "__main__":
    main()
