import json
import os
from typing import Any, Dict

class Storage:
    """
    Handle JSON-based persistence for the search index and metadata.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def save(self, data: Dict[str, Any]) -> None:
        """
        Save dictionary data to a JSON file.
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise IOError(f"Failed to save data to {self.filepath}: {e}")

    def load(self) -> Dict[str, Any]:
        """
        Load dictionary data from a JSON file.
        """
        if not os.path.exists(self.filepath):
            return {}

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise IOError(f"Failed to load data from {self.filepath}: {e}")

    def delete(self) -> None:
        """
        Delete the index file.
        """
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
