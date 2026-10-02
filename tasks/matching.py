import pandas as pd
from typing import Dict, Any
from .base import BaseTask
from ml.similarity import calculate_job_matching


class MatchingTask(BaseTask):
    name = "matching"
    description = "Resume to Job Description Similarity Matching Task"

    def validate(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        return len(df.columns) >= 2

    def execute(self, data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        resume_text = data.get("resume_text", "")
        job_description = data.get("job_description", "")
        use_embeddings = data.get("use_embeddings", False)
        return calculate_job_matching(resume_text, job_description, use_embeddings)
