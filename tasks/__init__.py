from typing import Dict, Type
from .base import BaseTask
from .classification import ClassificationTask
from .matching import MatchingTask
from .ranking import RankingTask
from .skill_extraction import SkillExtractionTask
from .scoring import ScoringTask, RecommendationTask, RegressionTask, ClusteringTask

TASK_REGISTRY: Dict[str, Type[BaseTask]] = {
    "classification": ClassificationTask,
    "matching": MatchingTask,
    "ranking": RankingTask,
    "skill_extraction": SkillExtractionTask,
    "scoring": ScoringTask,
    "recommendation": RecommendationTask,
    "regression": RegressionTask,
    "clustering": ClusteringTask
}

__all__ = ["BaseTask", "TASK_REGISTRY"]
