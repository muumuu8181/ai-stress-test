import os
import tempfile
from csvtool.utils import detect_delimiter, write_rows

def test_detect_delimiter():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("name,age\nAlice,30\n")
        f_path = f.name
    assert detect_delimiter(f_path) == ','
    os.remove(f_path)

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("name\tage\nAlice\t30\n")
        f_path = f.name
    assert detect_delimiter(f_path) == '\t'
    os.remove(f_path)

def test_write_rows():
    rows = [{'name': 'Alice', 'age': '30'}, {'name': 'Bob', 'age': '25'}]
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f_path = f.name
    write_rows(iter(rows), filepath=f_path)
    with open(f_path, 'r') as f:
        content = f.read()
    assert 'name,age' in content
    assert 'Alice,30' in content
    os.remove(f_path)
