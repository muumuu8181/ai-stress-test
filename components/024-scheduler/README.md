# Job Scheduler

A simple, thread-based job scheduler for Python using only standard libraries.

## Features

- **Flexible Schedules**: cron-like, fixed intervals, and one-shot executions.
- **Job Priorities**: Higher priority jobs are executed first.
- **Dependencies**: Support for job dependencies where a job runs only after its dependencies complete successfully.
- **Retries**: Configurable retries with exponential backoff.
- **Concurrency**: Parallel execution using a thread pool.
- **History Tracking**: Recording of job execution results and status.
- **Graceful Shutdown**: Wait for running jobs to complete during shutdown.
- **Job Cancellation**: Cancel pending or running jobs.

## Installation

No external dependencies required. Simply include the `scheduler` package in your project.

## Usage

### Basic Usage

```python
import time
from scheduler.scheduler import Scheduler
from scheduler.job import Job
from scheduler.models import ScheduleType

def my_job(name):
    print(f"Hello, {name}!")
    return f"Finished {name}"

# Initialize scheduler
scheduler = Scheduler(max_workers=5)

# Add a one-shot job
job = Job(my_job, args=("World",), priority=10)
scheduler.add_job(job)

# Start the scheduler
scheduler.start()

# Wait for job completion
time.sleep(1)

# Check status and history
print(f"Job Status: {scheduler.get_job_status(job.job_id)}")
print(f"History: {scheduler.get_job_history(job.job_id)}")

# Stop the scheduler
scheduler.stop()
```

### Cron Schedule

```python
# Runs every minute
job = Job(my_job, args=("Cron",), schedule_type=ScheduleType.CRON, schedule_value="* * * * *")
scheduler.add_job(job)
```

### Interval Schedule

```python
# Runs every 10 seconds
job = Job(my_job, args=("Interval",), schedule_type=ScheduleType.INTERVAL, schedule_value=10)
scheduler.add_job(job)
```

### Dependencies

```python
job1 = Job(my_job, args=("Job 1",), job_id="j1")
job2 = Job(my_job, args=("Job 2",), job_id="j2", dependencies=["j1"])

scheduler.add_job(job1)
scheduler.add_job(job2) # job2 will wait for job1 to succeed
```

### Retries

```python
def failing_job():
    raise ValueError("Something went wrong")

job = Job(failing_job, max_retries=3, retry_delay=1.0, retry_backoff=2.0)
scheduler.add_job(job)
```

## Testing

Run tests using `pytest`:

```bash
PYTHONPATH=src pytest tests/
```

Check coverage:

```bash
PYTHONPATH=src coverage run -m pytest tests/
PYTHONPATH=src coverage report -m
```
