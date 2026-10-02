import os
import pytest
import pandas as pd
from ml.data_loader import load_dataset
from ml.data_profiler import profile_dataset
from ml.preprocessing import clean_text
from ml.skill_extractor import extract_skills
from ml.similarity import calculate_job_matching
from ml.ranking import rank_candidates
from ml.trainer import train_pipeline
from ml.predictor import Predictor


def test_data_loader():
    df = load_dataset("data/sample/sample_resumes.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "resume_text" in df.columns


def test_data_profiler():
    df = load_dataset("data/sample/sample_resumes.csv")
    profile = profile_dataset(df, target_col="job_role")
    assert profile["rows"] > 0
    assert profile["recommended_task"] == "classification"


def test_preprocessing():
    cleaned = clean_text("Hello WORLD!!! Check out https://example.com email@test.com 123-456-7890")
    assert "hello world" in cleaned
    assert "https" not in cleaned


def test_skill_extractor():
    res = extract_skills("Python developer with SQL, TensorFlow, AWS and Docker experience.")
    assert "Python" in res["skills"]
    assert "Sql" in res["skills"] or "SQL" in res["skills"]
    assert res["total_count"] >= 3


def test_job_matching():
    match = calculate_job_matching(
        "Senior Data Scientist with Python, SQL and Machine Learning experience.",
        "Looking for a Data Scientist with Python, SQL and AWS knowledge."
    )
    assert match["similarity_score"] > 0
    assert "Python" in match["matching_skills"]


def test_candidate_ranking():
    candidates = [
        {"candidate_id": "c1", "candidate_name": "Alice", "resume_text": "Python SQL Data Scientist"},
        {"candidate_id": "c2", "candidate_name": "Bob", "resume_text": "Java Spring Boot Backend Developer"}
    ]
    rankings = rank_candidates(candidates, "Data Scientist with Python and SQL")
    assert len(rankings) == 2
    assert rankings[0]["candidate_name"] == "Alice"


def test_train_and_predict():
    meta = train_pipeline(data_path="data/sample/sample_resumes.csv", target_col="job_role", task_type="classification")
    assert meta["model"] is not None

    predictor = Predictor()
    assert predictor.is_ready
    pred = predictor.predict_single("Senior Machine Learning Engineer skilled in Python PyTorch.")
    assert "prediction" in pred
    assert pred["confidence"] > 0
