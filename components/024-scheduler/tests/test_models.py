from datetime import datetime
from scheduler.models import JobStatus, ScheduleType, JobHistory

def test_job_status_enum():
    assert JobStatus.PENDING.value == "pending"
    assert JobStatus.RUNNING.value == "running"
    assert JobStatus.SUCCESS.value == "success"
    assert JobStatus.FAILED.value == "failed"
    assert JobStatus.RETRYING.value == "retrying"
    assert JobStatus.CANCELLED.value == "cancelled"

def test_schedule_type_enum():
    assert ScheduleType.CRON.value == "cron"
    assert ScheduleType.INTERVAL.value == "interval"
    assert ScheduleType.ONE_SHOT.value == "one_shot"

def test_job_history_dataclass():
    now = datetime.now()
    history = JobHistory(
        job_id="job1",
        run_id="run1",
        status=JobStatus.SUCCESS,
        start_time=now,
        end_time=now,
        return_value=42
    )
    assert history.job_id == "job1"
    assert history.run_id == "run1"
    assert history.status == JobStatus.SUCCESS
    assert history.start_time == now
    assert history.end_time == now
    assert history.return_value == 42
    assert history.error is None
