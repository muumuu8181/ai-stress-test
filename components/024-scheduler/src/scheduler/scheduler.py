import threading
import time
import datetime
import uuid
import queue
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, List, Optional, Any, Callable
from .models import JobStatus, ScheduleType, JobHistory
from .job import Job

logger = logging.getLogger(__name__)

class Scheduler:
    """Manages scheduling and execution of jobs."""

    def __init__(self, max_workers: int = 5):
        """
        Initialize the Scheduler.

        Args:
            max_workers: Maximum number of worker threads for job execution.
        """
        self.jobs: Dict[str, Job] = {}
        self.history: List[JobHistory] = []
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._stop_event = threading.Event()
        self._scheduler_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._job_futures: Dict[str, Future] = {}

    def add_job(self, job: Job) -> str:
        """
        Add a job to the scheduler.

        Args:
            job: The job instance to add.

        Returns:
            The job ID.
        """
        with self._lock:
            self.jobs[job.job_id] = job
        return job.job_id

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.

        Args:
            job_id: The ID of the job to cancel.

        Returns:
            True if the job was cancelled, False otherwise.
        """
        with self._lock:
            if job_id not in self.jobs:
                return False
            job = self.jobs[job_id]
            job.status = JobStatus.CANCELLED
            if job_id in self._job_futures:
                self._job_futures[job_id].cancel()
            return True

    def start(self):
        """Start the scheduler background thread."""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return
        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()

    def stop(self, wait: bool = True):
        """
        Stop the scheduler.

        Args:
            wait: Whether to wait for running jobs to complete.
        """
        self._stop_event.set()
        if self._scheduler_thread:
            self._scheduler_thread.join()
        self._executor.shutdown(wait=wait)

    def _run_scheduler(self):
        """Main loop for the scheduler thread."""
        while not self._stop_event.is_set():
            now = datetime.datetime.now()
            jobs_to_run = []

            with self._lock:
                for job in self.jobs.values():
                    if job.status == JobStatus.CANCELLED:
                        continue
                    if job.should_run(now):
                        # Check dependencies
                        dependencies_satisfied = True
                        for dep_id in job.dependencies:
                            dep_job = self.jobs.get(dep_id)
                            if not dep_job or dep_job.status != JobStatus.SUCCESS:
                                dependencies_satisfied = False
                                break

                        if dependencies_satisfied:
                            jobs_to_run.append(job)

            # Sort by priority (higher first)
            jobs_to_run.sort(key=lambda j: j.priority, reverse=True)

            for job in jobs_to_run:
                self._submit_job(job)

            time.sleep(0.01) # Reduced sleep time for better precision

    def _submit_job(self, job: Job):
        """Submit a job for execution."""
        with self._lock:
            if job.status == JobStatus.RUNNING:
                return
            job.status = JobStatus.RUNNING
            run_id = str(uuid.uuid4())
            job.last_run_id = run_id

            future = self._executor.submit(self._execute_job, job, run_id)
            self._job_futures[job.job_id] = future

    def _execute_job(self, job: Job, run_id: str):
        """Execute a job and handle its result."""
        start_time = datetime.datetime.now()
        history = JobHistory(job_id=job.job_id, run_id=run_id, status=JobStatus.RUNNING, start_time=start_time)

        # We can't safely kill a thread in Python.
        # For timeout, we use another thread to wait for the job.
        job_result_queue = queue.Queue()

        def wrapper():
            try:
                res = job.func(*job.args, **job.kwargs)
                job_result_queue.put(("success", res))
            except Exception as e:
                job_result_queue.put(("error", e))

        job_thread = threading.Thread(target=wrapper, daemon=True)
        job_thread.start()

        try:
            status, result_or_err = job_result_queue.get(timeout=job.timeout)

            with self._lock:
                # Only update if job status is still RUNNING (not CANCELLED)
                if job.status != JobStatus.RUNNING:
                    return

                if status == "success":
                    job.status = JobStatus.SUCCESS
                    job.retries_count = 0
                    history.status = JobStatus.SUCCESS
                    history.return_value = result_or_err

                    # Update next run time before setting status to PENDING
                    job.update_next_run_time(datetime.datetime.now())

                    # If it's a recurring job, reset to PENDING so it can run again
                    if job.schedule_type in [ScheduleType.INTERVAL, ScheduleType.CRON]:
                        job.status = JobStatus.PENDING
                else:
                    raise result_or_err
        except queue.Empty:
            # Timeout occurred
            with self._lock:
                if job.status != JobStatus.RUNNING:
                    return

                error_msg = f"Job {job.job_id} timed out after {job.timeout}s"
                if job.retries_count < job.max_retries:
                    job.status = JobStatus.RETRYING
                    job.retries_count += 1
                    delay = job.get_retry_delay()
                    job.next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=delay)
                    history.status = JobStatus.RETRYING
                else:
                    job.status = JobStatus.FAILED
                    history.status = JobStatus.FAILED

                history.error = error_msg
                logger.error(error_msg)
        except Exception as e:
            with self._lock:
                if job.status != JobStatus.RUNNING:
                    return

                if job.retries_count < job.max_retries:
                    job.status = JobStatus.RETRYING
                    job.retries_count += 1
                    delay = job.get_retry_delay()
                    job.next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=delay)
                    history.status = JobStatus.RETRYING
                else:
                    job.status = JobStatus.FAILED
                    history.status = JobStatus.FAILED

                history.error = str(e)
                logger.error(f"Job {job.job_id} failed: {e}")
        finally:
            history.end_time = datetime.datetime.now()
            with self._lock:
                self.history.append(history)
                if job.job_id in self._job_futures:
                    del self._job_futures[job.job_id]

    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """Get the current status of a job."""
        with self._lock:
            job = self.jobs.get(job_id)
            return job.status if job else None

    def get_job_history(self, job_id: Optional[str] = None) -> List[JobHistory]:
        """Get the execution history of jobs."""
        with self._lock:
            if job_id:
                return [h for h in self.history if h.job_id == job_id]
            return list(self.history)
