import json
import os
from maze_gen.maze import Maze, CellType
from maze_gen.io import to_ascii, to_pbm
from maze_gen.serialization import to_json, from_json

def test_ascii_output():
    maze = Maze(2, 2)
    maze.set_cell(1, 1, CellType.PATH)
    maze.set_cell(1, 2, CellType.PATH)
    maze.set_cell(1, 3, CellType.PATH)
    ascii_out = to_ascii(maze)
    assert 'S' in ascii_out
    assert 'G' in ascii_out
    assert '#' in ascii_out

def test_pbm_output(tmp_path):
    maze = Maze(2, 2)
    filepath = tmp_path / "test.pbm"
    to_pbm(maze, str(filepath))
    assert os.path.exists(filepath)
    with open(filepath, 'r') as f:
        content = f.read()
        assert content.startswith("P1")

def test_json_serialization():
    maze = Maze(3, 3)
    maze.set_cell(2, 2, CellType.PATH)
    json_str = to_json(maze)
    data = json.loads(json_str)
    assert data['width'] == 3
    assert data['height'] == 3

    new_maze = from_json(json_str)
    assert new_maze.width == 3
    assert new_maze.height == 3
    assert new_maze.get_cell(2, 2) == CellType.PATH
