"""Member 1: Extract text from resume PDFs into the canonical dataset CSV.

Outputs:
  data/processed/resumes.csv        (resume_id, filename, category, text)
  reports/eda/extraction_report.json
  reports/eda/extraction_failures.csv   (only if failures exist)

Deterministic: PDFs are processed in sorted (category, path) order and IDs
are assigned sequentially, so rerunning on the same input produces the same
exact outputs.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_DIR = PROJECT_ROOT / "data" / "raw" / "resume_dataset" / "data" / "data"


def normalize_extracted_text(text: str) -> str:
    """Normalize whitespace problems from raw PDF extraction."""
    if not isinstance(text, str):
        return ""
    # Normalize line breaks, collapse runs of spaces/tabs, strip per-line.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(line)
    # Collapse 3+ consecutive blank lines into one blank line.
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(path: Path) -> str:
    """Extract text page-by-page preserving page order."""
    pages = []
    with pymupdf.open(str(path)) as doc:
        for page in doc:
            pages.append(page.get_text("text") or "")
    return normalize_extracted_text("\n".join(pages))


def find_pdfs(root: Path):
    return sorted(root.rglob("*.pdf"), key=lambda p: (p.parent.name, p.name))


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract resume PDFs to CSV.")
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "processed" / "resumes.csv")
    parser.add_argument("--report", type=Path, default=PROJECT_ROOT / "reports" / "eda" / "extraction_report.json")
    parser.add_argument("--failures", type=Path, default=PROJECT_ROOT / "reports" / "eda" / "extraction_failures.csv")
    args = parser.parse_args()

    if not args.dataset_dir.exists():
        print(f"ERROR: dataset dir not found: {args.dataset_dir}", file=sys.stderr)
        return 1

    pdfs = find_pdfs(args.dataset_dir)
    print(f"Found {len(pdfs)} PDF files under {args.dataset_dir}")

    rows = []
    failures = []
    empty_count = 0
    category_counts = {}
    total_len = 0
    counter = 0

    for path in pdfs:
        category = path.parent.name.strip()
        try:
            text = extract_pdf_text(path)
        except Exception as exc:  # corrupted PDF: record and continue
            failures.append({"filename": path.name, "category": category, "error": str(exc)})
            continue

        if len(text.strip()) == 0:
            empty_count += 1

        counter += 1
        resume_id = f"RF-{counter:06d}"
        rows.append({"resume_id": resume_id, "filename": path.name, "category": category, "text": text})
        category_counts[category] = category_counts.get(category, 0) + 1
        total_len += len(text)

    # Write canonical CSV
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["resume_id", "filename", "category", "text"])
        writer.writeheader()
        writer.writerows(rows)

    # Write failures CSV only if failures exist
    if failures:
        args.failures.parent.mkdir(parents=True, exist_ok=True)
        with open(args.failures, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["filename", "category", "error"])
            writer.writeheader()
            writer.writerows(failures)

    report = {
        "total_files": len(pdfs),
        "successful_extractions": len(rows),
        "failed_extractions": len(failures),
        "empty_extractions": empty_count,
        "categories": sorted(category_counts.keys()),
        "category_counts": dict(sorted(category_counts.items())),
        "average_text_length": round(total_len / max(len(rows), 1), 2),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(json.dumps({k: v for k, v in report.items() if k != "category_counts"}, indent=2))
    print(f"Wrote {args.output}")
    print(f"Wrote {args.report}")
    if failures:
        print(f"Wrote {args.failures} ({len(failures)} failures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
