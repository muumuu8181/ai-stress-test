import os
import subprocess
import time
import pytest

def test_cli_execution(tmp_path):
    os.chdir(tmp_path)
    tasks_file = tmp_path / "tasks.yaml"
    tasks_file.write_text("""
tasks:
  build:
    cmds:
      - echo "Building" > out.txt
""")

    result = subprocess.run(["python3", "-m", "taskrunner", "-f", str(tasks_file)], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Running 'build'" in result.stdout
    assert (tmp_path / "out.txt").read_text().strip() == "Building"

def test_incremental_build(tmp_path):
    os.chdir(tmp_path)
    source = tmp_path / "source.txt"
    target = tmp_path / "target.txt"
    source.write_text("v1")

    tasks_file = tmp_path / "tasks.yaml"
    tasks_file.write_text(f"""
tasks:
  build:
    sources: [{str(source)}]
    targets: [{str(target)}]
    cmds:
      - cp {str(source)} {str(target)}
""")

    # First run
    result = subprocess.run(["python3", "-m", "taskrunner", "-f", str(tasks_file)], capture_output=True, text=True)
    assert "Running 'build'" in result.stdout
    assert target.read_text() == "v1"

    # Second run (no changes)
    result = subprocess.run(["python3", "-m", "taskrunner", "-f", str(tasks_file)], capture_output=True, text=True)
    assert "Skipping 'build'" in result.stdout

    # Change source
    time.sleep(0.1)
    source.write_text("v2")
    result = subprocess.run(["python3", "-m", "taskrunner", "-f", str(tasks_file)], capture_output=True, text=True)
    assert "Running 'build'" in result.stdout
    assert target.read_text() == "v2"

def test_parallel_execution(tmp_path):
    os.chdir(tmp_path)
    tasks_file = tmp_path / "tasks.yaml"
    # Task 1 and 2 take some time and can run in parallel
    tasks_file.write_text("""
tasks:
  t1:
    cmds:
      - python3 -c 'import time; time.sleep(0.5)'
      - touch t1_done
  t2:
    cmds:
      - python3 -c 'import time; time.sleep(0.5)'
      - touch t2_done
  final:
    deps: [t1, t2]
    cmds: [touch final_done]
""")

    start_time = time.time()
    # We use -B to force execution
    result = subprocess.run(["python3", "-m", "taskrunner", "-f", str(tasks_file), "-j", "2", "-B", "final"], capture_output=True, text=True)
    end_time = time.time()

    assert result.returncode == 0
    assert (tmp_path / "t1_done").exists()
    assert (tmp_path / "t2_done").exists()
    assert (tmp_path / "final_done").exists()
    # If parallel, it should take around 0.5s + overhead, not 1.0s.
    # Allowing some margin for startup time.
    duration = end_time - start_time
    assert duration < 1.0, f"Parallel execution took too long: {duration}"

def test_dry_run(tmp_path):
    os.chdir(tmp_path)
    tasks_file = tmp_path / "tasks.yaml"
    tasks_file.write_text("""
tasks:
  test:
    cmds: [touch test_file]
""")
    result = subprocess.run(["python3", "-m", "taskrunner", "-f", str(tasks_file), "-n"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "(dry-run) touch test_file" in result.stdout
    assert not (tmp_path / "test_file").exists()

def test_list_tasks(tmp_path):
    os.chdir(tmp_path)
    tasks_file = tmp_path / "tasks.yaml"
    tasks_file.write_text("""
tasks:
  t1:
    deps: [t2]
  t2:
    cmds: [echo]
""")
    result = subprocess.run(["python3", "-m", "taskrunner", "-f", str(tasks_file), "-l"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "t1                   t2" in result.stdout
    assert "t2" in result.stdout
