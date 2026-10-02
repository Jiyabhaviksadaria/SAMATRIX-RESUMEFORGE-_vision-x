import os
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, Dict, Any


def load_dataset(file_path: str) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found at: {file_path}")

    ext = path.suffix.lower()
    if ext == ".csv":
        # Try multiple encodings for robustness
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        df = None
        for enc in encodings:
            try:
                df = pd.read_csv(path, encoding=enc)
                break
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue

        if df is None:
            # Fallback using python engine
            df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip", engine="python")
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported dataset format: {ext}. Supported formats: .csv, .xlsx, .xls")

    if df.empty:
        raise ValueError("Dataset is empty.")

    # Clean column names (strip whitespace)
    df.columns = [str(c).strip() for c in df.columns]

    # Remove duplicate columns if any
    df = df.loc[:, ~df.columns.duplicated()]

    return df
