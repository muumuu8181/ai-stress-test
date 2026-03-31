import argparse
import sys
import os
from .parser import parse_file
from .core import Runner

def main():
    parser = argparse.ArgumentParser(description="A simple Make-like task runner.")
    parser.add_argument(
        "tasks",
        metavar="TASK",
        type=str,
        nargs="*",
        help="Tasks to run (default: first task in file)"
    )
    parser.add_argument(
        "-f", "--file",
        default="tasks.yaml",
        help="Task definition file (default: tasks.yaml)"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List available tasks"
    )
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Show commands without running them"
    )
    parser.add_argument(
        "-B", "--force",
        action="store_true",
        help="Always run all tasks"
    )
    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=1,
        help="Number of parallel jobs"
    )

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: Task file '{args.file}' not found.")
        sys.exit(1)

    try:
        tasks = parse_file(args.file)
    except Exception as e:
        print(f"Error parsing task file: {e}")
        sys.exit(1)

    if args.list:
        print("Available tasks:")
        for task in tasks:
            print(f"  {task.name:20} {', '.join(task.dependencies)}")
        return

    runner = Runner(
        tasks=tasks,
        dry_run=args.dry_run,
        force=args.force,
        parallel=args.jobs
    )

    target_tasks = args.tasks
    if not target_tasks and tasks:
        # Default to the first task
        target_tasks = [tasks[0].name]

    success = runner.run(target_tasks)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
