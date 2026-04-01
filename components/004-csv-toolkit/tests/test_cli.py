import os
import tempfile
import pytest
import io
from csvtool.cli import main

@pytest.fixture
def csv_file():
    fd, path = tempfile.mkstemp(suffix='.csv')
    with os.fdopen(fd, 'w') as f:
        f.write("id,name,age\n1,Alice,30\n2,Bob,25\n3,Charlie,35\n")
    yield path
    os.remove(path)

def test_cli_select_direct(csv_file):
    f = io.StringIO()
    main(['select', '--columns', 'name,age', csv_file], stdout=f)
    output = f.getvalue()
    assert "name,age" in output
    assert "Alice,30" in output

def test_cli_filter_direct(csv_file):
    f = io.StringIO()
    main(['filter', '--where', 'age > 30', csv_file], stdout=f)
    output = f.getvalue()
    assert "Charlie,35" in output
    assert "Alice" not in output

def test_cli_join_direct(csv_file):
    fd, other_path = tempfile.mkstemp(suffix='.csv')
    with os.fdopen(fd, 'w') as f:
        f.write("id,city\n1,New York\n2,Los Angeles\n")

    f = io.StringIO()
    main(['join', '--on', 'id', csv_file, other_path], stdout=f)
    output = f.getvalue()
    assert "New York" in output
    assert "Los Angeles" in output
    os.remove(other_path)

def test_cli_stats_direct(csv_file):
    f = io.StringIO()
    main(['stats', csv_file], stdout=f)
    output = f.getvalue()
    assert '"row_count": 3' in output
    assert '"avg": 30' in output

def test_cli_help():
    f = io.StringIO()
    main([], stdout=f)
    assert "usage: csvtool" in f.getvalue()

def test_cli_filter_invalid():
    f = io.StringIO()
    with pytest.raises(SystemExit):
        main(['filter', '--where', 'invalid', 'dummy.csv'], stdout=f)
