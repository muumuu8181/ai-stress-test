from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class Job:
    """Represents a job in a CI pipeline."""
    name: str
    run: str
    allow_failure: bool = False
    timeout: Optional[int] = None # in seconds
    if_cond: Optional[str] = None
    unless_cond: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], default_name: str) -> 'Job':
        """Creates a Job instance from a dictionary."""
        return cls(
            name=data.get('name', default_name),
            run=data.get('run', ''),
            allow_failure=data.get('allow_failure', False),
            timeout=data.get('timeout'),
            if_cond=data.get('if'),
            unless_cond=data.get('unless'),
            artifacts=data.get('artifacts', []),
            env=data.get('env', {})
        )

@dataclass
class Stage:
    """Represents a stage in a CI pipeline."""
    name: str
    jobs: List[Job] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stage':
        """Creates a Stage instance from a dictionary."""
        name = data.get('name', 'unnamed_stage')
        jobs_data = data.get('jobs', [])
        jobs = []
        for i, job_data in enumerate(jobs_data):
            if isinstance(job_data, str):
                # Simple run: command
                job = Job(name=f"job_{i}", run=job_data)
            elif isinstance(job_data, dict):
                job = Job.from_dict(job_data, f"job_{i}")
            else:
                continue
            jobs.append(job)
        return cls(name=name, jobs=jobs)

@dataclass
class Pipeline:
    """Represents a full CI pipeline."""
    stages: List[Stage] = field(default_factory=list)
    vars: Dict[str, str] = field(default_factory=dict)
    env: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pipeline':
        """Creates a Pipeline instance from a dictionary."""
        stages_data = data.get('stages', [])
        stages = [Stage.from_dict(s) for s in stages_data if isinstance(s, dict)]
        return cls(
            stages=stages,
            vars=data.get('vars', {}),
            env=data.get('env', {})
        )
