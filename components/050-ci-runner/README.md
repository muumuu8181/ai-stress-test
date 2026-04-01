# Simple CI Pipeline Runner (050-ci-runner)

A lightweight CI pipeline runner implemented using only the Python standard library. It supports YAML-defined stages, parallel job execution, environment variables, variable expansion, conditions (`if`/`unless`), timeouts, and artifacts.

## Features

- **YAML Configuration**: Define your pipeline using a simple YAML format.
- **Sequential Stages**: Stages are executed one by one.
- **Parallel Jobs**: Jobs within the same stage can run concurrently.
- **Variable Expansion**: Use `${VAR}` for workflow variables and `${env.VAR}` for environment variables.
- **Conditions**: Conditional execution of jobs using `if` and `unless` expressions.
- **Timeouts**: Prevent jobs from running forever with the `timeout` setting.
- **Artifacts**: Verify and report on generated files.
- **Real-time Logging**: Watch job output as it happens.
- **JSON Reports**: Generate detailed execution reports including logs and timings.

## Pipeline Definition (`pipeline.yaml`)

```yaml
vars:
  PROJECT_NAME: "my_ci_project"

env:
  PYTHON_VERSION: "3.12"

stages:
  - name: test
    jobs:
      - name: unit_tests
        run: "pytest tests/"
        timeout: 60
      - name: linting
        run: "flake8 src/"
        allow_failure: true
  - name: build
    jobs:
      - name: package
        run: "python setup.py sdist"
        if: "${env.CI} == 'true'"
        artifacts:
          - dist/*.tar.gz
```

## Usage

Run the CI runner using the command line:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/components/050-ci-runner
python3 -m cirunner pipeline.yaml --report report.json
```

### Command Line Arguments

- `pipeline_file`: Path to the pipeline YAML file (default: `pipeline.yaml`).
- `--report`, `-r`: Path to save the JSON execution report.

## Requirements

- Python 3.12+ (Standard library only)

## Development and Testing

Run tests with `pytest`:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/components/050-ci-runner
python3 -m pytest components/050-ci-runner/tests/
```

Check coverage:

```bash
python3 -m pytest components/050-ci-runner/tests/ --cov=cirunner
```
