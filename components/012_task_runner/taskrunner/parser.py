import re
from typing import Dict, Any, List, Optional
from .core import Task

class Parser:
    """
    A simple YAML-like DSL parser for task runner files.
    Supports only a subset of YAML: mappings, lists, and indentation.
    """

    def __init__(self, content: str):
        self.lines = content.splitlines()
        self.index = 0

    def parse(self) -> Dict[str, Any]:
        """
        Parses the entire content.

        Returns:
            A dictionary containing global variables and task definitions.
        """
        result = {
            "vars": {},
            "tasks": {}
        }

        while self.index < len(self.lines):
            line = self.lines[self.index].strip()
            if not line or line.startswith("#"):
                self.index += 1
                continue

            if line == "vars:":
                self.index += 1
                result["vars"] = self._parse_mapping(0)
            elif line == "tasks:":
                self.index += 1
                result["tasks"] = self._parse_tasks(0)
            else:
                # Top level can also have direct mappings for simplicity
                if ":" in line:
                    key, value = self._parse_line(line)
                    if key == "vars":
                        self.index += 1
                        result["vars"] = self._parse_mapping(0)
                    elif key == "tasks":
                        self.index += 1
                        result["tasks"] = self._parse_tasks(0)
                self.index += 1

        return result

    def _get_indent(self, line: str) -> int:
        return len(line) - len(line.lstrip())

    def _parse_line(self, line: str) -> tuple[str, str]:
        if ":" not in line:
            return line.strip(), ""
        parts = line.split(":", 1)
        return parts[0].strip(), parts[1].strip()

    def _parse_mapping(self, parent_indent: int) -> Dict[str, str]:
        mapping = {}
        # Peek first indented line to determine section indent
        section_indent = -1

        while self.index < len(self.lines):
            line = self.lines[self.index]
            if not line.strip() or line.strip().startswith("#"):
                self.index += 1
                continue

            indent = self._get_indent(line)
            if indent <= parent_indent:
                break

            if section_indent == -1:
                section_indent = indent
            elif indent != section_indent:
                # Part of a nested structure or mismatch, handled by callers
                break

            key, value = self._parse_line(line)
            if value:
                mapping[key] = value
            self.index += 1
        return mapping

    def _parse_tasks(self, parent_indent: int) -> Dict[str, Dict[str, Any]]:
        tasks = {}
        section_indent = -1

        while self.index < len(self.lines):
            line = self.lines[self.index]
            if not line.strip() or line.strip().startswith("#"):
                self.index += 1
                continue

            indent = self._get_indent(line)
            if indent <= parent_indent:
                break

            if section_indent == -1:
                section_indent = indent
            elif indent != section_indent:
                break

            task_name, value = self._parse_line(line)
            self.index += 1
            # For tasks, we want the indentation of the first detail line
            # or at least something greater than task_name indent.
            tasks[task_name] = self._parse_task_details(indent)
        return tasks

    def _parse_task_details(self, task_indent: int) -> Dict[str, Any]:
        details = {}
        while self.index < len(self.lines):
            line = self.lines[self.index]
            if not line.strip() or line.strip().startswith("#"):
                self.index += 1
                continue

            indent = self._get_indent(line)
            if indent <= task_indent:
                break

            key, value = self._parse_line(line)
            if value:
                # Check if it's a list or a string
                if value.startswith("[") and value.endswith("]"):
                    # Basic list parsing: [a, b, c]
                    details[key] = [i.strip() for i in value[1:-1].split(",") if i.strip()]
                else:
                    details[key] = value
                self.index += 1
            else:
                self.index += 1
                # Check next line for list or mapping
                details[key] = self._parse_list_or_mapping(indent)
        return details

    def _parse_list_or_mapping(self, parent_indent: int) -> Any:
        # Look ahead for indent
        items = []
        mapping = {}
        is_list = False
        is_mapping = False

        start_index = self.index
        while self.index < len(self.lines):
            line = self.lines[self.index]
            if not line.strip() or line.strip().startswith("#"):
                self.index += 1
                continue

            indent = self._get_indent(line)
            if indent <= parent_indent:
                break

            stripped = line.strip()
            if stripped.startswith("- "):
                is_list = True
                items.append(stripped[2:].strip())
                self.index += 1
            elif ":" in stripped:
                is_mapping = True
                key, value = self._parse_line(stripped)
                mapping[key] = value
                self.index += 1
            else:
                self.index += 1

        if is_list:
            return items
        if is_mapping:
            return mapping
        return None

def parse_file(filepath: str) -> List[Task]:
    """
    Parses a task runner file and returns a list of Task objects.
    """
    with open(filepath, 'r') as f:
        content = f.read()

    parser = Parser(content)
    parsed_data = parser.parse()

    global_vars = parsed_data.get("vars", {})
    tasks_data = parsed_data.get("tasks", {})

    tasks = []
    for name, data in tasks_data.items():
        task = Task(
            name=name,
            dependencies=data.get("deps") or data.get("dependencies"),
            commands=data.get("cmds") or data.get("commands"),
            sources=data.get("sources"),
            targets=data.get("targets"),
            variables=data.get("vars")
        )
        task.expand_variables(global_vars)
        tasks.append(task)

    return tasks
