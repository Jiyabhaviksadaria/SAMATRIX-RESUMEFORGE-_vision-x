import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.data_loader import load_dataset
from ml.data_profiler import profile_dataset
from ml.config import get_config


def main():
    config = get_config()
    data_path = sys.argv[1] if len(sys.argv) > 1 else config["dataset"]["path"]

    print(f"\n==========================================")
    print(f" RESUMEFORGE AI — DATASET PROFILER")
    print(f"==========================================")
    print(f"Loading dataset from: {data_path}")

    try:
        df = load_dataset(data_path)
        profile = profile_dataset(df)

        print(f"\n✓ Dataset loaded successfully")
        print(f"✓ Rows: {profile['rows']:,}")
        print(f"✓ Columns: {profile['columns']}")
        print(f"✓ Text Columns: {profile['text_columns']}")
        print(f"✓ Categorical Columns: {profile['categorical_columns']}")
        print(f"✓ Numerical Columns: {profile['numeric_columns']}")
        print(f"✓ Target Candidates: {profile['possible_target_columns']}")
        print(f"✓ Recommended Task: {profile['recommended_task'].upper()} (Confidence: {profile['confidence']*100:.0f}%)")
        print(f"  Reasoning: {profile['reason']}")

        if profile["warnings"]:
            print(f"\n⚠️  Warnings:")
            for w in profile["warnings"]:
                print(f"   - {w}")

        print("\nColumn Summary:")
        for col in profile["columns_detail"]:
            print(f"   - {col['name']:<20} | Type: {col['dtype']:<10} | Missing: {col['missing_count']:<5} | Unique: {col['unique_count']}")

        print(f"\n==========================================")

    except Exception as e:
        print(f"❌ Error profiling dataset: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
