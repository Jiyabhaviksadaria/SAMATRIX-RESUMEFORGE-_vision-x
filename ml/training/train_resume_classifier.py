"""
Member 2: leakage-safe resume classification training pipeline.

Improved version:
- Word TF-IDF unigrams + bigrams
- Character TF-IDF 3-5 grams
- Combined sparse features
- Linear SVM + Logistic Regression
- Model selection by validation Macro-F1
"""

from pathlib import Path
import html
import json
import re
import time

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.sparse import hstack

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC


ROOT = Path(__file__).resolve().parents[2]

DEFAULT_INPUTS = [
    ROOT / "data" / "processed" / "resumes.csv",
    ROOT / "data" / "Resume.csv",
    ROOT / "data" / "resume.csv",
]

MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports" / "models"


def clean_text(value: object) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", " ", text)

    # Keep technical characters such as +, # and . for C++, C#, .NET.
    text = re.sub(r"[^A-Za-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()

    return text


def load_dataset(path: Path | None = None) -> pd.DataFrame:
    if path is None:
        for candidate in DEFAULT_INPUTS:
            if candidate.exists():
                path = candidate
                break

    if path is None or not path.exists():
        raise FileNotFoundError(
            "Dataset not found. Expected data/processed/resumes.csv or data/Resume.csv."
        )

    df = pd.read_csv(path)

    # Normalize known schemas.
    if {"Resume_str", "Category"}.issubset(df.columns):
        out = pd.DataFrame(
            {
                "resume_id": (
                    df["ID"] if "ID" in df.columns else np.arange(len(df))
                ),
                "filename": (
                    df["ID"].astype(str) if "ID" in df.columns else ""
                ),
                "category": df["Category"].astype(str),
                "text": df["Resume_str"].fillna("").astype(str),
            }
        )

    elif {"text", "category"}.issubset(df.columns):
        out = pd.DataFrame(
            {
                "resume_id": (
                    df["resume_id"]
                    if "resume_id" in df.columns
                    else np.arange(len(df))
                ),
                "filename": (
                    df["filename"] if "filename" in df.columns else ""
                ),
                "category": df["category"].astype(str),
                "text": df["text"].fillna("").astype(str),
            }
        )

    else:
        raise ValueError(
            f"Unsupported columns: {list(df.columns)}. "
            "Expected Resume_str/Category or text/category."
        )

    out["clean_text"] = out["text"].map(clean_text)

    out = out[out["clean_text"].str.len() >= 20].copy()
    out = out.drop_duplicates(subset=["clean_text"]).reset_index(drop=True)

    if out["category"].nunique() < 2:
        raise ValueError("Need at least two target categories.")

    return out


def split_data(df: pd.DataFrame):
    # 70% train, 15% validation, 15% test.
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["category"],
    )

    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["category"],
    )

    return train_df, val_df, test_df


def evaluate(model, X, y_true):
    pred = model.predict(X)

    return {
        "accuracy": accuracy_score(y_true, pred),
        "precision_weighted": precision_score(
            y_true,
            pred,
            average="weighted",
            zero_division=0,
        ),
        "recall_weighted": recall_score(
            y_true,
            pred,
            average="weighted",
            zero_division=0,
        ),
        "f1_weighted": f1_score(
            y_true,
            pred,
            average="weighted",
            zero_division=0,
        ),
        "f1_macro": f1_score(
            y_true,
            pred,
            average="macro",
            zero_division=0,
        ),
        "predictions": pred,
    }


def train(data_path: str | None = None):
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_dataset(Path(data_path) if data_path else None)

    train_df, val_df, test_df = split_data(df)

    encoder = LabelEncoder()
    encoder.fit(df["category"])

    y_train = encoder.transform(train_df["category"])
    y_val = encoder.transform(val_df["category"])
    y_test = encoder.transform(test_df["category"])

    print("\nFEATURE EXTRACTION")
    print("Word TF-IDF + Character TF-IDF")

    # ---------------------------------------------------------
    # WORD TF-IDF
    # ---------------------------------------------------------
    word_vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.98,
        sublinear_tf=True,
        max_features=150000,
    )

    X_train_word = word_vectorizer.fit_transform(
        train_df["clean_text"]
    )

    X_val_word = word_vectorizer.transform(
        val_df["clean_text"]
    )

    X_test_word = word_vectorizer.transform(
        test_df["clean_text"]
    )

    # ---------------------------------------------------------
    # CHARACTER TF-IDF
    # ---------------------------------------------------------
    char_vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        min_df=2,
        max_features=100000,
        sublinear_tf=True,
    )

    X_train_char = char_vectorizer.fit_transform(
        train_df["clean_text"]
    )

    X_val_char = char_vectorizer.transform(
        val_df["clean_text"]
    )

    X_test_char = char_vectorizer.transform(
        test_df["clean_text"]
    )

    # ---------------------------------------------------------
    # COMBINE FEATURES
    # ---------------------------------------------------------
    X_train = hstack(
        [X_train_word, X_train_char],
        format="csr",
    )

    X_val = hstack(
        [X_val_word, X_val_char],
        format="csr",
    )

    X_test = hstack(
        [X_test_word, X_test_char],
        format="csr",
    )

    print(f"Word features: {X_train_word.shape[1]}")
    print(f"Character features: {X_train_char.shape[1]}")
    print(f"Combined features: {X_train.shape[1]}")

    candidates = {
        "Logistic Regression": LogisticRegression(
            max_iter=2500,
            class_weight="balanced",
            C=2.0,
            random_state=42,
        ),
        "Linear SVM": LinearSVC(
            C=1.5,
            class_weight="balanced",
            random_state=42,
            dual="auto",
        ),
    }

    rows = []
    fitted = {}

    for name, model in candidates.items():

        print(f"\nTraining: {name}")

        start = time.time()

        model.fit(X_train, y_train)

        elapsed = time.time() - start

        val = evaluate(model, X_val, y_val)
        test = evaluate(model, X_test, y_test)

        rows.append(
            {
                "model": name,
                "validation_accuracy": val["accuracy"],
                "validation_f1_macro": val["f1_macro"],
                "validation_f1_weighted": val["f1_weighted"],
                "test_accuracy": test["accuracy"],
                "test_precision_weighted": test[
                    "precision_weighted"
                ],
                "test_recall_weighted": test[
                    "recall_weighted"
                ],
                "test_f1_macro": test["f1_macro"],
                "test_f1_weighted": test["f1_weighted"],
                "train_seconds": elapsed,
            }
        )

        fitted[name] = (
            model,
            test["predictions"],
        )

    comparison = pd.DataFrame(rows).sort_values(
        ["validation_f1_macro", "validation_accuracy"],
        ascending=False,
    )

    comparison.to_csv(
        REPORT_DIR / "model_comparison.csv",
        index=False,
    )

    best_name = comparison.iloc[0]["model"]

    best_model, best_pred = fitted[best_name]

    # ---------------------------------------------------------
    # FINAL CLASSIFICATION REPORT
    # ---------------------------------------------------------
    report = classification_report(
        y_test,
        best_pred,
        labels=np.arange(len(encoder.classes_)),
        target_names=encoder.classes_,
        output_dict=True,
        zero_division=0,
    )

    pd.DataFrame(report).T.to_csv(
        REPORT_DIR / "classification_report.csv"
    )

    # ---------------------------------------------------------
    # CONFUSION MATRIX
    # ---------------------------------------------------------
    cm = confusion_matrix(
        y_test,
        best_pred,
        labels=np.arange(len(encoder.classes_)),
    )

    fig_w = max(
        12,
        len(encoder.classes_) * 0.55,
    )

    fig_h = max(
        10,
        len(encoder.classes_) * 0.45,
    )

    fig, ax = plt.subplots(
        figsize=(fig_w, fig_h)
    )

    im = ax.imshow(
        cm,
        interpolation="nearest",
    )

    ax.figure.colorbar(
        im,
        ax=ax,
    )

    ax.set(
        xticks=np.arange(len(encoder.classes_)),
        yticks=np.arange(len(encoder.classes_)),
        xticklabels=encoder.classes_,
        yticklabels=encoder.classes_,
        ylabel="Actual",
        xlabel="Predicted",
        title=f"Confusion Matrix — {best_name}",
    )

    plt.setp(
        ax.get_xticklabels(),
        rotation=90,
        ha="center",
    )

    fig.tight_layout()

    fig.savefig(
        REPORT_DIR / "confusion_matrix.png",
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(fig)

    # ---------------------------------------------------------
    # ERROR ANALYSIS
    # ---------------------------------------------------------
    error_mask = best_pred != y_test

    error_df = test_df.loc[
        error_mask,
        [
            "resume_id",
            "filename",
            "category",
            "text",
        ],
    ].copy()

    error_df["predicted_category"] = (
        encoder.inverse_transform(
            best_pred[error_mask]
        )
    )

    error_df["text_preview"] = (
        error_df["text"]
        .str.replace(
            r"\s+",
            " ",
            regex=True,
        )
        .str.slice(0, 500)
    )

    error_df[
        [
            "resume_id",
            "filename",
            "category",
            "predicted_category",
            "text_preview",
        ]
    ].to_csv(
        REPORT_DIR / "error_analysis.csv",
        index=False,
    )

    # ---------------------------------------------------------
    # SAVE MODELS
    # ---------------------------------------------------------
    joblib.dump(
        best_model,
        MODEL_DIR / "best_model.joblib",
    )

    joblib.dump(
        {
            "word": word_vectorizer,
            "char": char_vectorizer,
        },
        MODEL_DIR / "vectorizer.joblib",
    )

    joblib.dump(
        encoder,
        MODEL_DIR / "label_encoder.joblib",
    )

    # ---------------------------------------------------------
    # METADATA
    # ---------------------------------------------------------
    best_row = comparison.iloc[0].to_dict()

    metadata = {
        "model": best_name,
        "task": "multiclass_resume_classification",
        "feature": "combined word + character TF-IDF",
        "word_tfidf": {
            "analyzer": "word",
            "ngram_range": [1, 2],
            "min_df": 2,
            "max_df": 0.98,
            "sublinear_tf": True,
            "max_features": 150000,
        },
        "char_tfidf": {
            "analyzer": "char",
            "ngram_range": [3, 5],
            "min_df": 2,
            "sublinear_tf": True,
            "max_features": 100000,
        },
        "split": {
            "train": len(train_df),
            "validation": len(val_df),
            "test": len(test_df),
            "random_state": 42,
        },
        "classes": encoder.classes_.tolist(),
        "metrics": {
            k: float(v)
            for k, v in best_row.items()
            if isinstance(
                v,
                (
                    int,
                    float,
                    np.integer,
                    np.floating,
                ),
            )
        },
    }

    (
        MODEL_DIR / "metadata.json"
    ).write_text(
        json.dumps(
            metadata,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nDATASET")
    print(f"Rows used: {len(df)}")
    print(f"Classes: {len(encoder.classes_)}")
    print(
        f"Train/Val/Test: "
        f"{len(train_df)}/"
        f"{len(val_df)}/"
        f"{len(test_df)}"
    )

    print("\nMODEL COMPARISON")
    print(
        comparison.to_string(
            index=False
        )
    )

    print(
        f"\nBEST MODEL: {best_name}"
    )

    print(
        f"Test Macro F1: "
        f"{best_row['test_f1_macro']:.4f}"
    )

    print(
        f"Test Weighted F1: "
        f"{best_row['test_f1_weighted']:.4f}"
    )

    print(
        f"Test Accuracy: "
        f"{best_row['test_accuracy']:.4f}"
    )

    return metadata


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data",
        default=None,
    )

    args = parser.parse_args()

    train(args.data)