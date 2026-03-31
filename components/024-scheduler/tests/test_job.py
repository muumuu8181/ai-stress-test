import datetime
import pytest
from scheduler.job import Job
from scheduler.models import JobStatus, ScheduleType

def dummy_func(x):
    return x * 2

def test_job_initialization():
    job = Job(dummy_func, args=(10,), priority=5)
    assert job.func == dummy_func
    assert job.args == (10,)
    assert job.priority == 5
    assert job.status == JobStatus.PENDING
    assert job.job_id is not None

def test_one_shot_next_run_time():
    now = datetime.datetime.now()
    job = Job(dummy_func, schedule_type=ScheduleType.ONE_SHOT)
    # The initialization calls update_next_run_time
    assert job.next_run_time is not None
    assert job.next_run_time >= now

def test_interval_next_run_time():
    now = datetime.datetime.now()
    job = Job(dummy_func, schedule_type=ScheduleType.INTERVAL, schedule_value=60)
    assert job.next_run_time is not None
    assert job.next_run_time >= now

    first_run_time = job.next_run_time
    job.update_next_run_time(now + datetime.timedelta(seconds=1))
    assert job.next_run_time == first_run_time + datetime.timedelta(seconds=60)

def test_cron_next_run_time():
    job = Job(dummy_func, schedule_type=ScheduleType.CRON, schedule_value="0 10 * * *")
    assert job.next_run_time is not None
    assert job.next_run_time.hour == 10
    assert job.next_run_time.minute == 0

def test_should_run():
    job = Job(dummy_func, schedule_type=ScheduleType.ONE_SHOT)
    now = datetime.datetime.now()
    job.next_run_time = now + datetime.timedelta(seconds=60)
    assert not job.should_run(now)
    assert job.should_run(now + datetime.timedelta(seconds=61))

def test_retry_delay():
    job = Job(dummy_func, max_retries=3, retry_delay=1.0, retry_backoff=2.0)
    assert job.get_retry_delay() == 1.0
    job.retries_count = 1
    assert job.get_retry_delay() == 2.0
    job.retries_count = 2
    assert job.get_retry_delay() == 4.0

def test_invalid_interval():
    with pytest.raises(ValueError):
        Job(dummy_func, schedule_type=ScheduleType.INTERVAL, schedule_value="invalid")
