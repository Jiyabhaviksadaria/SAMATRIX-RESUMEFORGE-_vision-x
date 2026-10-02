from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, List, Optional


class BaseTask(ABC):
    """Abstract Base Class for all Resume Intelligence task plugins."""
    name: str = "base_task"
    description: str = "Base Resume Intelligence Task"

    @abstractmethod
    def validate(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        """Validates if the dataset supports this task."""
        pass

    @abstractmethod
    def execute(self, data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """Executes task processing."""
        pass
