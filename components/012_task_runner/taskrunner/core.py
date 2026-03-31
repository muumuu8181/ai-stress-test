import os
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from typing import List, Dict, Optional, Any, Set
from pathlib import Path

class Task:
    """
    Represents a single task in the task runner.
    """

    def __init__(
        self,
        name: str,
        dependencies: List[str] = None,
        commands: List[str] = None,
        sources: List[str] = None,
        targets: List[str] = None,
        variables: Dict[str, str] = None,
    ):
        """
        Initializes a Task.

        Args:
            name: Name of the task.
            dependencies: List of task names this task depends on.
            commands: List of shell commands to execute.
            sources: List of source files.
            targets: List of target files.
            variables: Local variables for this task.
        """
        self.name = name
        self.dependencies = dependencies or []
        self.commands = commands or []
        self.sources = sources or []
        self.targets = targets or []
        self.variables = variables or {}

    def expand_variables(self, global_vars: Dict[str, str]) -> None:
        """
        Expands variables in commands, sources, and targets using ${VAR} syntax.
        Variables are looked up in task-local variables, then global variables,
        and finally environment variables.

        Args:
            global_vars: Global variables defined in the task file.
        """
        # Priority: Task variables > Global variables > Environment variables
        vars_to_use = {**os.environ, **global_vars, **self.variables}

        def replace(match: re.Match) -> str:
            var_name = match.group(1)
            return vars_to_use.get(var_name, match.group(0))

        pattern = re.compile(r"\$\{([^}]+)\}")

        self.commands = [pattern.sub(replace, cmd) for cmd in self.commands]
        self.sources = [pattern.sub(replace, src) for src in self.sources]
        self.targets = [pattern.sub(replace, tgt) for tgt in self.targets]
        self.dependencies = [pattern.sub(replace, dep) for dep in self.dependencies]

    def is_up_to_date(self) -> bool:
        """
        Checks if the task is up-to-date based on file timestamps.
        A task is up-to-date if all targets exist and all targets are newer
        than all sources.

        Returns:
            True if up-to-date, False otherwise.
        """
        if not self.targets:
            return False

        # If any target is missing, it's not up-to-date
        for target in self.targets:
            if not os.path.exists(target):
                return False

        if not self.sources:
            # If no sources, and targets exist, we consider it up-to-date
            return True

        # Find the oldest target
        oldest_target_time = min(os.path.getmtime(target) for target in self.targets)

        # Find the newest source
        for source in self.sources:
            if not os.path.exists(source):
                # If a source doesn't exist, we can't verify, so it's not up-to-date
                return False

        newest_source_time = max(os.path.getmtime(source) for source in self.sources)

        return oldest_target_time >= newest_source_time

    def __repr__(self) -> str:
        return f"Task(name={self.name}, dependencies={self.dependencies})"

class TaskGraph:
    """
    Represents a directed acyclic graph (DAG) of tasks.
    """

    def __init__(self, tasks: List[Task]):
        self.tasks = {task.name: task for task in tasks}
        self.adj = {task.name: task.dependencies for task in tasks}

    def get_execution_order(self, target_tasks: List[str] = None) -> List[Task]:
        """
        Performs a topological sort to find the correct execution order.

        Args:
            target_tasks: The tasks to execute. If None, all tasks are included.

        Returns:
            A list of Task objects in topological order.

        Raises:
            ValueError: If a cycle is detected or a dependency is missing.
        """
        if not target_tasks:
            target_tasks = list(self.tasks.keys())

        # First, find all reachable tasks from target_tasks
        reachable = set()
        stack = list(target_tasks)
        while stack:
            node = stack.pop()
            if node not in reachable:
                if node not in self.tasks:
                    raise ValueError(f"Task '{node}' not found in task definitions.")
                reachable.add(node)
                stack.extend(self.tasks[node].dependencies)

        # Kahn's algorithm or DFS for topological sort
        visited = set()
        temp_visited = set()
        order = []

        def visit(node: str):
            if node in temp_visited:
                raise ValueError(f"Circular dependency detected involving task '{node}'.")
            if node not in visited:
                temp_visited.add(node)
                for dep in self.tasks[node].dependencies:
                    visit(dep)
                temp_visited.remove(node)
                visited.add(node)
                order.append(self.tasks[node])

        for node in sorted(reachable):
            if node not in visited:
                visit(node)

        return order

class Runner:
    """
    Executes tasks in the specified order.
    """

    def __init__(
        self,
        tasks: List[Task],
        dry_run: bool = False,
        force: bool = False,
        parallel: int = 1,
    ):
        self.graph = TaskGraph(tasks)
        self.dry_run = dry_run
        self.force = force
        self.parallel = parallel
        self.executed_tasks = set()

    def run(self, target_names: List[str] = None) -> bool:
        """
        Executes the tasks in the correct order.

        Args:
            target_names: Names of tasks to run.

        Returns:
            True if all tasks succeeded, False otherwise.
        """
        try:
            execution_order = self.graph.get_execution_order(target_names)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return False

        if not execution_order:
            print("No tasks to run.")
            return True

        # In non-parallel mode, execute tasks one by one
        if self.parallel <= 1:
            for i, task in enumerate(execution_order):
                if not self._should_run_task(task):
                    print(f"[{i+1}/{len(execution_order)}] Skipping '{task.name}' (up-to-date)")
                    continue

                print(f"[{i+1}/{len(execution_order)}] Running '{task.name}'...")
                if not self.run_task(task):
                    return False
            return True
        else:
            # Parallel execution will be handled in the next step
            return self._run_parallel(execution_order)

    def _should_run_task(self, task: Task) -> bool:
        if self.force:
            return True
        return not task.is_up_to_date()

    def run_task(self, task: Task) -> bool:
        """
        Executes a single task's commands.
        """
        if self.dry_run:
            for cmd in task.commands:
                print(f"  (dry-run) {cmd}")
            return True

        for cmd in task.commands:
            print(f"  {cmd}")
            result = subprocess.run(cmd, shell=True)
            if result.returncode != 0:
                print(f"Error: Command failed with return code {result.returncode}")
                return False
        return True

    def _run_parallel(self, execution_order: List[Task]) -> bool:
        """
        Executes tasks in parallel while respecting dependency constraints.
        """
        self.lock = threading.Lock()
        self.completed_tasks: Set[str] = set()
        self.started_count = 0
        self.failed = False

        total = len(execution_order)
        task_objs = {t.name: t for t in execution_order}

        # Build dependency reverse map
        dependents = {t.name: [] for t in execution_order}
        remaining_deps = {t.name: len(t.dependencies) for t in execution_order}
        for t in execution_order:
            for dep in t.dependencies:
                if dep in dependents:
                    dependents[dep].append(t.name)

        ready_tasks = [t.name for t in execution_order if remaining_deps[t.name] == 0]

        with ThreadPoolExecutor(max_workers=self.parallel) as executor:
            futures = {}

            def submit_task(task_name: str):
                task = task_objs[task_name]
                future = executor.submit(self._run_task_wrapper, task, total)
                futures[future] = task_name

            for name in ready_tasks:
                submit_task(name)

            while futures:
                done, _ = wait(futures.keys(), return_when=FIRST_COMPLETED)
                for future in done:
                    task_name = futures.pop(future)
                    try:
                        success = future.result()
                    except Exception as e:
                        print(f"Task '{task_name}' raised an exception: {e}", file=sys.stderr)
                        success = False

                    if not success:
                        self.failed = True

                    if not self.failed:
                        with self.lock:
                            self.completed_tasks.add(task_name)
                            for dependent in dependents[task_name]:
                                remaining_deps[dependent] -= 1
                                if remaining_deps[dependent] == 0:
                                    submit_task(dependent)

        return not self.failed

    def _run_task_wrapper(self, task: Task, total: int) -> bool:
        if self.failed:
            return False

        with self.lock:
            self.started_count += 1
            idx = self.started_count
            should_run = self._should_run_task(task)
            if not should_run:
                print(f"[{idx}/{total}] Skipping '{task.name}' (up-to-date)")
            else:
                print(f"[{idx}/{total}] Running '{task.name}'...")

        if not should_run:
            return True

        return self.run_task(task)
