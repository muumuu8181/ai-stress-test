import time
import pytest
import datetime
from scheduler.scheduler import Scheduler
from scheduler.job import Job
from scheduler.models import JobStatus, ScheduleType

def dummy_func(x):
    return x * 2

def error_func():
    raise ValueError("Error")

def sleep_func(duration):
    time.sleep(duration)
    return "done"

def test_add_and_get_job():
    scheduler = Scheduler()
    job = Job(dummy_func, args=(10,))
    job_id = scheduler.add_job(job)
    assert job_id == job.job_id
    assert scheduler.get_job_status(job_id) == JobStatus.PENDING

def test_scheduler_execution():
    scheduler = Scheduler()
    job = Job(dummy_func, args=(10,))
    scheduler.add_job(job)
    scheduler.start()

    # Wait for execution
    timeout = 2.0
    start_time = time.time()
    while time.time() - start_time < timeout:
        if scheduler.get_job_status(job.job_id) == JobStatus.SUCCESS:
            break
        time.sleep(0.1)

    assert scheduler.get_job_status(job.job_id) == JobStatus.SUCCESS
    history = scheduler.get_job_history(job.job_id)
    assert len(history) == 1
    assert history[0].status == JobStatus.SUCCESS
    assert history[0].return_value == 20

    scheduler.stop()

def test_scheduler_retry():
    scheduler = Scheduler()
    job = Job(error_func, max_retries=1, retry_delay=0.1)
    scheduler.add_job(job)
    scheduler.start()

    # Wait for first failure
    time.sleep(0.5)
    assert job.status in [JobStatus.RETRYING, JobStatus.FAILED]

    # Wait for retry and final failure
    time.sleep(0.5)
    assert scheduler.get_job_status(job.job_id) == JobStatus.FAILED
    assert len(scheduler.get_job_history(job.job_id)) == 2

    scheduler.stop()

def test_scheduler_priority():
    scheduler = Scheduler(max_workers=1)
    results = []

    def log_job(name, delay):
        time.sleep(delay)
        results.append(name)

    job_low = Job(log_job, args=("low", 0.1), priority=1)
    job_high = Job(log_job, args=("high", 0.1), priority=10)

    scheduler.add_job(job_low)
    scheduler.add_job(job_high)

    scheduler.start()
    time.sleep(1.0)

    # High priority should run first if they are both ready.
    assert results == ["high", "low"]

    scheduler.stop()

def test_cancel_job():
    scheduler = Scheduler()
    job = Job(dummy_func, args=(10,), schedule_type=ScheduleType.INTERVAL, schedule_value=60)
    scheduler.add_job(job)

    assert scheduler.cancel_job(job.job_id) is True
    assert job.status == JobStatus.CANCELLED

    scheduler.start()
    time.sleep(0.5)
    # Should not have run
    assert len(scheduler.get_job_history(job.job_id)) == 0

    scheduler.stop()

def test_job_timeout():
    scheduler = Scheduler()
    # Job takes 0.5s, timeout is 0.1s
    job = Job(sleep_func, args=(0.5,), timeout=0.1)
    scheduler.add_job(job)
    scheduler.start()

    # Wait
    time.sleep(1.0)

    assert scheduler.get_job_status(job.job_id) == JobStatus.FAILED
    history = scheduler.get_job_history(job.job_id)
    assert len(history) == 1
    assert history[0].status == JobStatus.FAILED
    assert "timed out" in history[0].error

    scheduler.stop()

def test_cancel_running_job():
    scheduler = Scheduler()
    def long_running():
        time.sleep(1.0)
        return "done"

    job = Job(long_running)
    scheduler.add_job(job)
    scheduler.start()

    # Wait for it to start
    time.sleep(0.2)
    assert scheduler.get_job_status(job.job_id) == JobStatus.RUNNING

    # Cancel it
    scheduler.cancel_job(job.job_id)
    assert job.status == JobStatus.CANCELLED

    # Wait for thread to finish
    time.sleep(1.0)
    # Status should still be CANCELLED, not SUCCESS
    assert scheduler.get_job_status(job.job_id) == JobStatus.CANCELLED

    scheduler.stop()
