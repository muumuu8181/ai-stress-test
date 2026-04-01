import os
import subprocess
import time
import threading
import re
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from .models import Pipeline, Stage, Job
from .conditions import should_run

@dataclass
class JobResult:
    job: Job
    status: str # 'passed', 'failed', 'skipped', 'timed_out'
    logs: str
    duration: float
    artifacts_found: List[str] = field(default_factory=list)

@dataclass
class StageResult:
    stage: Stage
    job_results: List[JobResult]
    status: str # 'passed', 'failed', 'skipped'

@dataclass
class PipelineResult:
    pipeline: Pipeline
    stage_results: List[StageResult]
    status: str # 'passed', 'failed'
    duration: float

class Executor:
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
        self.variables = pipeline.vars.copy()
        self.env = pipeline.env.copy()

    def run_job(self, job: Job) -> JobResult:
        """Executes a single job."""
        # Substitute variables in environment first to allow them to be used in conditions if needed
        # (Though current conditions.py uses self.env directly)

        # Merge job-specific environment
        current_env = self.env.copy()
        current_env.update(job.env)

        if not should_run(job.if_cond, job.unless_cond, self.variables, current_env):
            return JobResult(job, 'skipped', "Job skipped due to conditions.", 0.0)

        start_time = time.time()
        logs: List[str] = []
        status = 'passed'

        # Prepare environment for subprocess
        job_env = os.environ.copy()
        job_env.update(current_env)

        # Substitute variables in command
        command = self._substitute_vars(job.run, current_env)

        print(f"--- Running job: {job.name} ---")
        print(f"Command: {command}")

        try:
            # Popen for real-time logging and timeout
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=job_env,
                bufsize=1,
                universal_newlines=True
            )

            # Read logs in real-time
            def read_logs():
                if process.stdout:
                    for line in process.stdout:
                        print(f"[{job.name}] {line}", end='')
                        logs.append(line)

            log_thread = threading.Thread(target=read_logs)
            log_thread.start()

            try:
                process.wait(timeout=job.timeout)
                log_thread.join()
                if process.returncode != 0:
                    status = 'failed'
            except subprocess.TimeoutExpired:
                process.kill()
                log_thread.join()
                status = 'timed_out'
                logs.append(f"\nJob timed out after {job.timeout}s\n")

        except Exception as e:
            status = 'failed'
            logs.append(f"Error executing job: {str(e)}")

        duration = time.time() - start_time

        # Check artifacts
        artifacts_found = []
        for art_path in job.artifacts:
            if os.path.exists(art_path):
                artifacts_found.append(art_path)
            else:
                logs.append(f"Warning: Artifact not found: {art_path}\n")

        return JobResult(job, status, "".join(logs), duration, artifacts_found)

    def _substitute_vars(self, text: str, job_env: Dict[str, str]) -> str:
        pattern = r'\${(.*?)}'
        def replace_var(match):
            var_name = match.group(1).strip()
            if var_name.startswith('env.'):
                env_key = var_name[4:]
                return job_env.get(env_key, os.environ.get(env_key, ''))
            return self.variables.get(var_name, '')
        return re.sub(pattern, replace_var, text)

    def run_pipeline(self) -> PipelineResult:
        """Executes the full pipeline."""
        start_time = time.time()
        stage_results = []
        pipeline_status = 'passed'

        for stage in self.pipeline.stages:
            print(f"\n=== Stage: {stage.name} ===")

            job_results: List[JobResult] = []
            # Parallel execution of jobs within a stage
            with ThreadPoolExecutor(max_workers=max(1, len(stage.jobs))) as executor:
                # To maintain order of job results, we can use map or list of futures
                future_to_job = {executor.submit(self.run_job, job): job for job in stage.jobs}
                for future in as_completed(future_to_job):
                    job_results.append(future.result())

            # Sort job results back to original order if desired,
            # but usually it doesn't matter for the status.

            # Determine stage status
            stage_status = 'passed'
            for res in job_results:
                if res.status in ('failed', 'timed_out') and not res.job.allow_failure:
                    stage_status = 'failed'
                    break

            stage_results.append(StageResult(stage, job_results, stage_status))

            if stage_status == 'failed':
                pipeline_status = 'failed'
                print(f"Stage {stage.name} failed. Stopping pipeline.")
                break

        duration = time.time() - start_time
        return PipelineResult(self.pipeline, stage_results, pipeline_status, duration)
