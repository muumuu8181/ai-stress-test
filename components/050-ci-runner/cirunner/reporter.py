import json
from typing import Dict, Any
from .executor import PipelineResult

def generate_report(result: PipelineResult) -> Dict[str, Any]:
    """Generates a JSON-serializable report from the pipeline execution result."""
    report = {
        "status": result.status,
        "total_duration": result.duration,
        "stages": []
    }

    for stage_res in result.stage_results:
        stage_data = {
            "name": stage_res.stage.name,
            "status": stage_res.status,
            "jobs": []
        }

        for job_res in stage_res.job_results:
            job_data = {
                "name": job_res.job.name,
                "status": job_res.status,
                "duration": job_res.duration,
                "logs": job_res.logs,
                "artifacts": job_res.artifacts_found
            }
            stage_data["jobs"].append(job_data)

        report["stages"].append(stage_data)

    return report

def save_report(report: Dict[str, Any], filepath: str):
    """Saves the report to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2)
