import os
from pathlib import Path
from typing import Optional, List


def extract_text_from_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found at: {file_path}")

    ext = path.suffix.lower()

    if ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext == ".pdf":
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(path)
            extracted = []
            for page in reader.pages:
                txt = page.extract_text()
                if txt:
                    extracted.append(txt)
            return "\n".join(extracted)
        except Exception as e:
            print(f"[Warning] PDF extraction via PyPDF2 failed: {e}. Falling back to plain text read.")
            with open(path, "r", encoding="latin-1", errors="ignore") as f:
                return f.read()

    elif ext in [".docx", ".doc"]:
        try:
            import docx
            doc = docx.Document(path)
            return "\n".join([p.text for p in doc.paragraphs if p.text])
        except Exception as e:
            print(f"[Warning] DOCX extraction failed: {e}.")
            with open(path, "r", encoding="latin-1", errors="ignore") as f:
                return f.read()

    elif ext in [".csv", ".xlsx", ".xls"]:
        import pandas as pd
        from ml.data_loader import load_dataset
        df = load_dataset(str(path))
        return "\n".join(df.astype(str).values.flatten())

    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
