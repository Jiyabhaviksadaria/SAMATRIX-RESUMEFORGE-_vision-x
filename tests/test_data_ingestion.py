import json
from pathlib import Path

import pandas as pd
import pytest

from ml.preprocessing import preprocess_text
from scripts.data.extract_resumes import extract_pdf_text, normalize_extracted_text

ROOT = Path(__file__).resolve().parents[1]


def test_preprocess_text_empty_string():
    assert preprocess_text("") == ""


def test_preprocess_text_none_behaves_safely():
    assert preprocess_text(None) == ""


def test_preprocess_text_non_string():
    assert preprocess_text(123) == ""
    assert preprocess_text(["a"]) == ""


def test_preprocess_text_technical_tokens_survive():
    text = "Experienced in Python, C++, C#, .NET, SQL, AWS, NLP, TensorFlow, Java, JavaScript, Node.js, React, PyTorch, Keras."
    out = preprocess_text(text)
    for token in ["Python", "C++", "C#", ".NET", "SQL", "AWS", "NLP", "TensorFlow", "Java", "JavaScript", "Node.js", "React", "PyTorch", "Keras"]:
        assert token in out, token


def test_preprocess_text_html_and_artifacts_removed():
    out = preprocess_text("<p>Hello <b>World</b></p>\u200b\ufffd")
    assert "<" not in out and ">" not in out
    assert "Hello World" in out


def test_normalize_extracted_text_whitespace():
    out = normalize_extracted_text("a  b\t\tc\r\n\r\n\r\nd")
    assert "a b c" in out
    assert "\r" not in out


def test_extract_pdf_text_missing_file():
    with pytest.raises(Exception):
        extract_pdf_text(Path("does_not_exist.pdf"))


def test_canonical_dataset_csv_schema():
    csv_path = ROOT / "data" / "processed" / "resumes.csv"
    if not csv_path.exists():
        pytest.skip("resumes.csv not generated yet")
    df = pd.read_csv(csv_path)
    assert list(df.columns) == ["resume_id", "filename", "category", "text"]
    assert df["category"].notna().all()
    assert (df["category"].str.strip() != "").all()
    assert df["resume_id"].is_unique


def test_extraction_report_json():
    report_path = ROOT / "reports" / "eda" / "extraction_report.json"
    if not report_path.exists():
        pytest.skip("extraction report not generated yet")
    report = json.loads(report_path.read_text())
    for key in ["total_files", "successful_extractions", "failed_extractions", "empty_extractions", "categories", "category_counts", "average_text_length"]:
        assert key in report
    assert report["total_files"] == report["successful_extractions"] + report["failed_extractions"]
