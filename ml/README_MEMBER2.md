# Member 2 — ML Training Package

## Purpose

This package is the isolated ML contribution for ResumeForge.

It is deliberately separate from:
- Member 1: data extraction / EDA
- Member 3: backend / frontend

## Input contract

Preferred:

`data/processed/resumes.csv`

Columns:
- `resume_id`
- `filename`
- `category`
- `text`

It also accepts the existing `Resume.csv` schema:
- `ID`
- `Resume_str`
- `Resume_html`
- `Category`

## Training

From repository root:

```bash
python ml/training/train_resume_classifier.py
```

or:

```bash
python ml/training/train_resume_classifier.py --data data/processed/resumes.csv
```

## Outputs

```text
models/
  best_model.joblib
  vectorizer.joblib
  label_encoder.joblib
  metadata.json

reports/models/
  model_comparison.csv
  classification_report.csv
  confusion_matrix.png
  error_analysis.csv
```

## Leakage prevention

The pipeline:
1. splits raw text first;
2. fits TF-IDF only on training text;
3. transforms validation/test using the training vocabulary;
4. chooses the model using validation Macro-F1;
5. reports final metrics once on the untouched test set.

## Models

- Logistic Regression
- Linear SVM

Primary selection metric:
- validation Macro-F1

Final reporting:
- accuracy
- weighted precision
- weighted recall
- Macro-F1
- weighted F1

## Prediction contract for Member 3

```python
from ml.training.predict_resume import predict_resume

result = predict_resume(text)
```

Returns:

```json
{
  "category": "INFORMATION-TECHNOLOGY",
  "confidence": 0.91,
  "top_predictions": [
    {"category": "INFORMATION-TECHNOLOGY", "confidence": 0.91},
    {"category": "ENGINEERING", "confidence": 0.04},
    {"category": "CONSULTANT", "confidence": 0.02}
  ]
}
```

Note: SVM confidence is a normalized transformation of decision scores and should be presented as a relative model score, not a calibrated probability.
