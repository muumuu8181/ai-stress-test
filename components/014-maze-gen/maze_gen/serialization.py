import json
from .maze import Maze

def to_json(maze: Maze) -> str:
    """Serialize maze to JSON string."""
    return json.dumps(maze.to_dict())

def from_json(json_str: str) -> Maze:
    """Deserialize maze from JSON string."""
    return Maze.from_dict(json.loads(json_str))
