import pandas as pd
from typing import Dict, Any, List
from .base import BaseTask
from ml.ranking import rank_candidates


class RankingTask(BaseTask):
    name = "ranking"
    description = "Candidate Ranking & Match Matrix Task"

    def validate(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        return True

    def execute(self, data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        candidates: List[Dict[str, Any]] = data.get("candidates", [])
        job_description: str = data.get("job_description", "")
        rankings = rank_candidates(candidates, job_description)
        return {"rankings": rankings, "total_candidates": len(rankings)}
