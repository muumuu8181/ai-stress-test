import os
import tempfile
import pytest
from csvtool.core import CSVProcessor

@pytest.fixture
def csv_file():
    fd, path = tempfile.mkstemp(suffix='.csv')
    with os.fdopen(fd, 'w') as f:
        f.write("id,name,age,score\n1,Alice,30,95.5\n2,Bob,25,88.0\n3,Charlie,35,92.0\n")
    yield path
    os.remove(path)

def test_select(csv_file):
    processor = CSVProcessor(csv_file)
    rows = list(processor.select(['name', 'age']))
    assert len(rows) == 3
    assert 'name' in rows[0]
    assert 'id' not in rows[0]
    assert rows[0]['name'] == 'Alice'

def test_filter(csv_file):
    processor = CSVProcessor(csv_file)
    rows = list(processor.filter(lambda r: int(r['age']) > 30))
    assert len(rows) == 1
    assert rows[0]['name'] == 'Charlie'

def test_sort(csv_file):
    processor = CSVProcessor(csv_file)
    rows = list(processor.sort('age'))
    assert rows[0]['name'] == 'Bob'
    assert rows[-1]['name'] == 'Charlie'

def test_groupby(csv_file):
    processor = CSVProcessor(csv_file)
    # Add another row for grouping
    with open(csv_file, 'a') as f:
        f.write("4,David,30,80.0\n")

    rows = list(processor.groupby('age', {'score': 'avg', 'id': 'count'}))
    # Groups: age 30 (Alice, David), age 25 (Bob), age 35 (Charlie)
    group_30 = [r for r in rows if r['age'] == '30'][0]
    assert group_30['avg_score'] == (95.5 + 80.0) / 2
    assert group_30['count_id'] == 2

def test_join(csv_file):
    fd, other_path = tempfile.mkstemp(suffix='.csv')
    with os.fdopen(fd, 'w') as f:
        f.write("id,city\n1,New York\n2,Los Angeles\n")

    left_processor = CSVProcessor(csv_file)
    right_processor = CSVProcessor(other_path)

    # Inner Join
    rows = list(left_processor.join(right_processor, on_col='id', how='inner'))
    assert len(rows) == 2
    assert rows[0]['city'] == 'New York'

    # Left Join
    rows = list(left_processor.join(right_processor, on_col='id', how='left'))
    assert len(rows) == 3
    assert rows[2]['city'] is None

    os.remove(other_path)

def test_stats(csv_file):
    processor = CSVProcessor(csv_file)
    stats = processor.stats()
    assert stats['row_count'] == 3
    assert 'age' in stats['columns']
    assert stats['columns']['age']['avg'] == 30.0
