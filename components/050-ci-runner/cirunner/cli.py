import argparse
import sys
import os
from .parser import parse_yaml
from .models import Pipeline
from .executor import Executor
from .reporter import generate_report, save_report

def main():
    """Main CLI entry point for the CI runner."""
    parser = argparse.ArgumentParser(description="Simple CI Pipeline Runner")
    parser.add_argument('pipeline_file', nargs='?', default='pipeline.yaml', help="Path to the pipeline YAML file")
    parser.add_argument('--report', '-r', help="Path to save the JSON execution report")

    args = parser.parse_args()

    if not os.path.exists(args.pipeline_file):
        print(f"Error: Pipeline file not found: {args.pipeline_file}")
        sys.exit(1)

    try:
        with open(args.pipeline_file, 'r') as f:
            content = f.read()

        config = parse_yaml(content)
        pipeline = Pipeline.from_dict(config)

        executor = Executor(pipeline)
        result = executor.run_pipeline()

        report = generate_report(result)

        if args.report:
            save_report(report, args.report)
            print(f"\nReport saved to {args.report}")

        if result.status == 'failed':
            print("\nPipeline FAILED.")
            sys.exit(1)
        else:
            print("\nPipeline PASSED.")

    except Exception as e:
        print(f"Error executing pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
