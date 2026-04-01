import datetime
import pytest
from csvtool.schema import TypeInferrer, Schema

def test_type_inferrer():
    assert TypeInferrer.infer('10') == 10
    assert TypeInferrer.infer('3.14') == 3.14
    assert TypeInferrer.infer('true') is True
    assert TypeInferrer.infer('2023-05-20') == datetime.date(2023, 5, 20)
    assert TypeInferrer.infer('Hello') == 'Hello'

def test_schema_validation():
    schema = Schema({'name': str, 'age': int, 'score': float, 'active': bool, 'date': datetime.date})
    row = {'name': 'Alice', 'age': '30', 'score': '95.5', 'active': 'yes', 'date': '2023-05-20'}
    validated = schema.validate(row)
    assert validated['age'] == 30
    assert validated['score'] == 95.5
    assert validated['active'] is True
    assert validated['date'] == datetime.date(2023, 5, 20)

    with pytest.raises(ValueError):
        schema.validate({'name': 'Alice', 'age': 'thirty'}) # invalid age
