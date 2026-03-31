import time
import datetime
from scheduler.scheduler import Scheduler
from scheduler.job import Job
from scheduler.models import JobStatus, ScheduleType

def test_schedule_precision():
    scheduler = Scheduler()
    results = []

    def log_time():
        results.append(datetime.datetime.now())
        return True

    # Interval 0.1s
    job = Job(log_time, schedule_type=ScheduleType.INTERVAL, schedule_value=0.1)
    scheduler.add_job(job)

    scheduler.start()

    time.sleep(0.55)
    scheduler.stop()

    # We expect about 5-6 runs.
    # At start, then 0.1, 0.2, 0.3, 0.4, 0.5.
    assert len(results) >= 5

    # Check intervals between runs
    for i in range(len(results) - 1):
        diff = (results[i+1] - results[i]).total_seconds()
        # It won't be exact due to scheduler loop and thread switching,
        # but it should be close to 0.1s.
        assert 0.05 <= diff <= 0.15

def test_graceful_shutdown():
    scheduler = Scheduler()
    results = []

    def long_job():
        time.sleep(0.5)
        results.append("done")
        return True

    job = Job(long_job)
    scheduler.add_job(job)

    scheduler.start()

    # Wait for the job to start running
    timeout = 2.0
    start_time = time.time()
    while time.time() - start_time < timeout:
        if scheduler.get_job_status(job.job_id) == JobStatus.RUNNING:
            break
        time.sleep(0.05)

    assert scheduler.get_job_status(job.job_id) == JobStatus.RUNNING

    # Call stop and wait
    stop_start = time.time()
    scheduler.stop(wait=True)
    stop_duration = time.time() - stop_start

    # Should have waited for the long_job to complete
    assert "done" in results
    assert stop_duration >= 0.4
    assert scheduler.get_job_status(job.job_id) == JobStatus.SUCCESS
