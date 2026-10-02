import pandas as pd
from typing import Dict, Any
from .base import BaseTask
from ml.skill_extractor import extract_skills


class SkillExtractionTask(BaseTask):
    name = "skill_extraction"
    description = "Taxonomy Skill Extraction Task"

    def validate(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        return True

    def execute(self, data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        text = data.get("text", "")
        return extract_skills(text)
