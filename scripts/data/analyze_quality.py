"""Member 1: Dataset quality analysis + duplicate detection.

Reads data/processed/resumes.csv and writes
  reports/eda/data_quality.txt
  reports/eda/duplicates.csv (only if duplicates exist)
"""
import argparse
import csv
import re
from collections import Counter
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

VERY_SHORT_WORD_THRESHOLD = 50  # resumes with fewer words flagged as very short


def normalize_for_dup(text: str) -> str:
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "processed" / "resumes.csv")
    parser.add_argument("--report", type=Path, default=PROJECT_ROOT / "reports" / "eda" / "data_quality.txt")
    parser.add_argument("--duplicates", type=Path, default=PROJECT_ROOT / "reports" / "eda" / "duplicates.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    total = len(df)
    categories = df["category"].nunique()
    missing_text = int(df["text"].isna().sum())
    empty_text = int((df["text"].fillna("").str.strip() == "").sum())

    word_counts = df["text"].fillna("").apply(lambda t: len(str(t).split()))
    char_counts = df["text"].fillna("").str.len()

    very_short = int((word_counts < VERY_SHORT_WORD_THRESHOLD).sum())

    dup_filename_count = int(df["filename"].duplicated().sum())
    norm = df["text"].fillna("").apply(normalize_for_dup)
    exact_dup_mask = norm.duplicated(keep=False) & (norm != "")
    exact_duplicates = df[exact_dup_mask]
    duplicate_groups = int(exact_duplicates.groupby(norm[exact_dup_mask]).ngroups) if len(exact_duplicates) else 0
    exact_duplicate_count = int((exact_duplicates.groupby(norm[exact_dup_mask]).size() - 1).sum()) if len(exact_duplicates) else 0

    class_dist = df["category"].value_counts().sort_index()
    largest = class_dist.idxmax()
    smallest = class_dist.idxmin()

    lines = []
    lines.append("Dataset Summary")
    lines.append("---------------")
    lines.append(f"Total resumes: {total}")
    lines.append(f"Number of classes: {categories}")
    lines.append(f"Largest class: {largest} ({class_dist.max()})")
    lines.append(f"Smallest class: {smallest} ({class_dist.min()})")
    lines.append(f"Missing texts: {missing_text}")
    lines.append(f"Empty texts: {empty_text}")
    lines.append(f"Very short resumes (<{VERY_SHORT_WORD_THRESHOLD} words): {very_short}")
    lines.append(f"Duplicate filenames: {dup_filename_count}")
    lines.append(f"Exact duplicate texts: {exact_duplicate_count}")
    lines.append(f"Duplicate groups: {duplicate_groups}")
    lines.append("")
    lines.append("Text Length (words)")
    lines.append("-------------------")
    lines.append(f"Minimum: {int(word_counts.min())}")
    lines.append(f"Maximum: {int(word_counts.max())}")
    lines.append(f"Median: {int(word_counts.median())}")
    lines.append(f"Mean: {word_counts.mean():.2f}")
    lines.append("")
    lines.append("Text Length (characters)")
    lines.append("------------------------")
    lines.append(f"Minimum: {int(char_counts.min())}")
    lines.append(f"Maximum: {int(char_counts.max())}")
    lines.append(f"Median: {int(char_counts.median())}")
    lines.append(f"Mean: {char_counts.mean():.2f}")
    lines.append("")
    lines.append("Class Distribution")
    lines.append("------------------")
    for cat, n in class_dist.items():
        lines.append(f"{cat}: {n}")
    lines.append("")
    lines.append("Class Imbalance Note")
    lines.append("--------------------")
    ratio = class_dist.max() / max(class_dist.min(), 1)
    lines.append(f"Max/min class-size ratio: {ratio:.2f}. Minority classes are reported for Member 2; no resampling was applied.")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if len(exact_duplicates):
        dup = exact_duplicates[["resume_id", "filename", "category"]].copy()
        dup.to_csv(args.duplicates, index=False)

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
