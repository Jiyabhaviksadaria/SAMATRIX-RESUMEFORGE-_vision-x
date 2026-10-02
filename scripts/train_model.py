import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.trainer import train_pipeline
from ml.config import get_config


def main():
    config = get_config()
    print(f"\n==========================================")
    print(f" RESUMEFORGE AI — MODEL TRAINER")
    print(f"==========================================")

    data_path = sys.argv[1] if len(sys.argv) > 1 else config["dataset"]["path"]
    target_col = sys.argv[2] if len(sys.argv) > 2 else config["dataset"]["target"]

    print(f"Dataset: {data_path}")
    print(f"Target Column: {target_col}")

    try:
        metadata = train_pipeline(data_path=data_path, target_col=target_col)
        print(f"\n✓ Training completed successfully!")
        print(f"✓ Selected Best Model: {metadata['model']}")
        print(f"✓ Task: {metadata['task']}")
        print(f"✓ Train Rows: {metadata['train_rows']} | Test Rows: {metadata['test_rows']}")
        print(f"✓ Key Metrics:")
        for metric, score in metadata["metrics"].items():
            if isinstance(score, (int, float)):
                print(f"   - {metric.upper()}: {score}")

        print(f"\nModel Leaderboard:")
        for idx, item in enumerate(metadata["leaderboard"]):
            print(f"   #{idx+1} {item['name']:<25} | Score: {item['primary_score']:.4f} | Train Time: {item['train_time_sec']:.2f}s")

        print(f"\nArtifacts saved to: models/best_model.joblib")
        print(f"==========================================")
    except Exception as e:
        print(f"❌ Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
