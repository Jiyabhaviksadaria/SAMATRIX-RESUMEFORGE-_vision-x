import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

DEFAULT_SKILLS_PATH = Path(__file__).resolve().parent.parent / "data" / "skills.json"


class SkillExtractor:
    """Taxonomy-based skill extractor matching skills from text against configurable skills.json."""

    def __init__(self, skills_path: Optional[str] = None):
        self.skills_path = Path(skills_path) if skills_path else DEFAULT_SKILLS_PATH
        self.taxonomy: Dict[str, List[str]] = self._load_taxonomy()

    def _load_taxonomy(self) -> Dict[str, List[str]]:
        if self.skills_path.exists():
            try:
                with open(self.skills_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Warning] Failed to read skill taxonomy at {self.skills_path}: {e}")

        # Fallback taxonomy
        return {
            "Programming": ["python", "java", "c++", "javascript", "typescript", "sql", "html", "css"],
            "Machine Learning": ["scikit-learn", "tensorflow", "pytorch", "nlp", "machine learning", "deep learning"],
            "Data Science": ["pandas", "numpy", "power bi", "tableau", "statistics"],
            "Cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
            "Web": ["react", "next.js", "node.js", "fastapi", "django"]
        }

    def extract_skills(self, text: str) -> Dict[str, Any]:
        if not isinstance(text, str) or not text.strip():
            return {
                "skills": [],
                "categorized": {},
                "total_count": 0
            }

        text_lower = text.lower()
        extracted_skills = set()
        categorized: Dict[str, List[str]] = {}

        for category, skill_list in self.taxonomy.items():
            categorized[category] = []
            for skill in skill_list:
                # Regex word boundary check (handling special chars like c++, .net)
                escaped = re.escape(skill)
                pattern = r'(?:\b|(?<=\W))' + escaped + r'(?:\b|(?=\W))'
                if re.search(pattern, text_lower):
                    formatted_skill = skill.title() if len(skill) > 3 else skill.upper()
                    extracted_skills.add(formatted_skill)
                    categorized[category].append(formatted_skill)

            if not categorized[category]:
                del categorized[category]

        sorted_skills = sorted(list(extracted_skills))
        return {
            "skills": sorted_skills,
            "categorized": categorized,
            "total_count": len(sorted_skills)
        }


def extract_skills(text: str, skills_path: Optional[str] = None) -> Dict[str, Any]:
    extractor = SkillExtractor(skills_path)
    return extractor.extract_skills(text)
