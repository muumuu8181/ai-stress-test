# Task Runner (Make-like)

A simple, Python-only task runner inspired by `Make`. It supports task dependencies, variable expansion, incremental execution based on file timestamps, and parallel execution.

## Features

- **YAML/DSL format**: Define tasks in a simple YAML-like structure.
- **Dependency Graph (DAG)**: Automatically resolves task execution order and detects cycles.
- **Incremental Execution**: Skips tasks if target files are newer than source files.
- **Variable Expansion**: Supports `${VAR}` syntax with local, global, and environment variable support.
- **Parallel Execution**: Run independent tasks concurrently using `-j`.
- **Dry-run Mode**: Preview commands without executing them.
- **Progress Reporting**: Displays progress as tasks are executed.

## Usage

### Task Definition (`tasks.yaml`)

```yaml
vars:
  PROJECT: my_project
  CC: gcc

tasks:
  all:
    deps: [build]

  build:
    deps: [prepare]
    cmds:
      - ${CC} -o build/main main.c
    sources:
      - main.c
    targets:
      - build/main

  prepare:
    cmds:
      - mkdir -p build

  clean:
    cmds:
      - rm -rf build
```

### CLI Commands

Run the default task (the first task defined in the file):
```bash
python3 -m taskrunner
```

Run a specific task:
```bash
python3 -m taskrunner build
```

List available tasks:
```bash
python3 -m taskrunner -l
```

Dry-run mode (show commands without running):
```bash
python3 -m taskrunner -n build
```

Force re-run (ignore timestamps):
```bash
python3 -m taskrunner -B build
```

Parallel execution (run up to 4 jobs):
```bash
python3 -m taskrunner -j 4 build
```

Specify a custom task file:
```bash
python3 -m taskrunner -f my_tasks.yaml
```

## Requirements

- Python 3.12+
- Standard library only (no external dependencies required to run)

## Development and Testing

Run tests:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
pytest components/012_task_runner/tests/
```

Check coverage:
```bash
coverage run --source=components/012_task_runner/taskrunner -m pytest components/012_task_runner/tests/
coverage report
```
