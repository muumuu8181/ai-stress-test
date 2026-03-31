import time
from scheduler.scheduler import Scheduler
from scheduler.job import Job
from scheduler.models import JobStatus, ScheduleType

def test_job_dependencies():
    scheduler = Scheduler(max_workers=2)
    results = []

    def log_job(name):
        results.append(name)
        return True

    job1 = Job(log_job, args=("job1",), job_id="job1")
    job2 = Job(log_job, args=("job2",), job_id="job2", dependencies=["job1"])
    job3 = Job(log_job, args=("job3",), job_id="job3", dependencies=["job1", "job2"])

    # Add in different order to test dependency checking
    scheduler.add_job(job3)
    scheduler.add_job(job2)
    scheduler.add_job(job1)

    scheduler.start()

    # Wait for completion
    timeout = 2.0
    start_time = time.time()
    while time.time() - start_time < timeout:
        if scheduler.get_job_status("job3") == JobStatus.SUCCESS:
            break
        time.sleep(0.1)

    assert results == ["job1", "job2", "job3"]
    assert scheduler.get_job_status("job1") == JobStatus.SUCCESS
    assert scheduler.get_job_status("job2") == JobStatus.SUCCESS
    assert scheduler.get_job_status("job3") == JobStatus.SUCCESS

    scheduler.stop()

def test_job_dependency_failure():
    scheduler = Scheduler(max_workers=2)
    results = []

    def fail_job():
        raise ValueError("Failed")

    def success_job():
        results.append("success")
        return True

    job1 = Job(fail_job, job_id="job1")
    job2 = Job(success_job, job_id="job2", dependencies=["job1"])

    scheduler.add_job(job1)
    scheduler.add_job(job2)

    scheduler.start()

    # Wait
    time.sleep(1.0)

    assert scheduler.get_job_status("job1") == JobStatus.FAILED
    # job2 should still be PENDING because job1 failed
    assert scheduler.get_job_status("job2") == JobStatus.PENDING
    assert results == []

    scheduler.stop()

def test_recurring_job_dependency():
    scheduler = Scheduler(max_workers=2)
    results = []

    def recurring_job():
        results.append("recurring")
        return "recurring_res"

    def dependent_job():
        results.append("dependent")
        return "dependent_res"

    # Recurring every 0.1s
    job1 = Job(recurring_job, job_id="job1", schedule_type=ScheduleType.INTERVAL, schedule_value=0.1)
    # Dependent only on job1's first success
    job2 = Job(dependent_job, job_id="job2", dependencies=["job1"])

    scheduler.add_job(job1)
    scheduler.add_job(job2)

    scheduler.start()

    # Wait for job2 to succeed
    timeout = 2.0
    start_time = time.time()
    while time.time() - start_time < timeout:
        if scheduler.get_job_status("job2") == JobStatus.SUCCESS:
            break
        time.sleep(0.1)

    assert scheduler.get_job_status("job2") == JobStatus.SUCCESS
    assert "recurring" in results
    assert "dependent" in results

    scheduler.stop()
