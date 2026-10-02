import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional


class TaskDetector:
    """Task detector analyzing dataset schema to suggest ML task type."""

    @staticmethod
    def detect_task(df: pd.DataFrame, target_col: Optional[str] = None) -> Tuple[str, float, str]:
        if target_col and target_col in df.columns:
            target_series = df[target_col].dropna()
            n_unique = target_series.nunique()
            is_numeric = pd.api.types.is_numeric_dtype(target_series)

            if not is_numeric or n_unique <= 50:
                if n_unique <= 100:
                    return "classification", 0.95, f"Column '{target_col}' contains categorical or discrete values ({n_unique} unique classes)."
            if is_numeric and n_unique > 15:
                return "regression", 0.90, f"Column '{target_col}' is numerical with continuous values ({n_unique} unique values)."

        # Inspect all columns for target candidates
        text_cols = TaskDetector.find_text_columns(df)
        cat_cols = TaskDetector.find_categorical_columns(df)
        num_cols = TaskDetector.find_numeric_columns(df)

        if text_cols and cat_cols:
            return "classification", 0.85, f"Dataset has text column(s) ({', '.join(text_cols)}) and categorical target candidate ({cat_cols[0]})."
        elif len(text_cols) >= 2:
            return "matching", 0.80, f"Dataset contains multiple text columns ({', '.join(text_cols[:2])}) suitable for text matching."
        elif text_cols and not cat_cols and not num_cols:
            return "skill_extraction", 0.75, "Dataset primarily consists of unstructured text columns."
        elif num_cols and not cat_cols:
            return "clustering", 0.70, "Dataset contains numerical attributes suitable for unsupervised clustering."

        return "classification", 0.60, "Fallback assumption based on available text and categorical data."

    @staticmethod
    def find_text_columns(df: pd.DataFrame) -> List[str]:
        text_cols = []
        for col in df.columns:
            if pd.api.types.is_string_dtype(df[col]) or df[col].dtype == 'object':
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    avg_len = non_null.astype(str).str.len().mean()
                    if avg_len >= 30:  # Long text candidate
                        text_cols.append(col)
        return text_cols

    @staticmethod
    def find_categorical_columns(df: pd.DataFrame) -> List[str]:
        cat_cols = []
        for col in df.columns:
            n_unique = df[col].nunique()
            if (pd.api.types.is_string_dtype(df[col]) or df[col].dtype == 'object') and n_unique <= 100:
                avg_len = df[col].dropna().astype(str).str.len().mean() if len(df[col].dropna()) > 0 else 0
                if avg_len < 30:  # Short category/role name
                    cat_cols.append(col)
            elif pd.api.types.is_integer_dtype(df[col]) and 2 <= n_unique <= 20:
                cat_cols.append(col)
        return cat_cols

    @staticmethod
    def find_numeric_columns(df: pd.DataFrame) -> List[str]:
        return [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]


def profile_dataset(df: pd.DataFrame, target_col: Optional[str] = None) -> Dict[str, Any]:
    """Generates comprehensive dataset profiling report."""
    n_rows, n_cols = df.shape
    duplicate_rows = int(df.duplicated().sum())

    text_cols = TaskDetector.find_text_columns(df)
    cat_cols = TaskDetector.find_categorical_columns(df)
    num_cols = TaskDetector.find_numeric_columns(df)

    columns_detail = []
    missing_values = {}
    possible_targets = []

    for col in df.columns:
        series = df[col]
        missing_cnt = int(series.isna().sum())
        missing_ratio = float(missing_cnt / n_rows) if n_rows > 0 else 0.0
        unique_cnt = int(series.nunique())

        if missing_cnt > 0:
            missing_values[col] = missing_cnt

        dtype_str = str(series.dtype)
        columns_detail.append({
            "name": col,
            "dtype": dtype_str,
            "missing_count": missing_cnt,
            "missing_ratio": round(missing_ratio, 4),
            "unique_count": unique_cnt
        })

        # Target candidate evaluation
        if col in cat_cols or (col in num_cols and unique_cnt <= 100 and unique_cnt > 1):
            if col not in text_cols:
                possible_targets.append(col)

    # Class distribution and imbalance analysis
    selected_target = target_col if (target_col and target_col in df.columns) else (possible_targets[0] if possible_targets else None)
    class_dist = {}
    imbalance_info = {"status": "Unknown", "ratio": 1.0}

    if selected_target and selected_target in df.columns:
        val_counts = df[selected_target].value_counts().to_dict()
        class_dist = {str(k): int(v) for k, v in val_counts.items()}
        if len(val_counts) > 1:
            max_c = max(val_counts.values())
            min_c = min(val_counts.values())
            ratio = round(max_c / max(min_c, 1), 2)
            if ratio > 5.0:
                status = "Severe imbalance"
            elif ratio > 2.0:
                status = "Mild imbalance"
            else:
                status = "Balanced"
            imbalance_info = {"status": status, "ratio": ratio}

    recommended_task, confidence, reason = TaskDetector.detect_task(df, selected_target)

    warnings = []
    if duplicate_rows > 0:
        warnings.append(f"Found {duplicate_rows} duplicate row(s) in dataset.")
    if missing_values:
        warnings.append(f"Missing values detected in {len(missing_values)} column(s).")
    if imbalance_info.get("status") == "Severe imbalance":
        warnings.append("Severe class imbalance detected. Evaluation metrics like F1-Score are recommended over Accuracy.")

    return {
        "rows": n_rows,
        "columns": n_cols,
        "columns_detail": columns_detail,
        "text_columns": text_cols,
        "numeric_columns": num_cols,
        "categorical_columns": cat_cols,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "possible_target_columns": possible_targets,
        "selected_target": selected_target,
        "class_distribution": class_dist,
        "imbalance": imbalance_info,
        "recommended_task": recommended_task,
        "confidence": confidence,
        "reason": reason,
        "warnings": warnings
    }
