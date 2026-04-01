import pytest
from mock_server.models import Request
from mock_server.history import RequestHistory

def test_history_find():
    req1 = Request(method="GET", path="/a", headers={}, body=b"")
    req2 = Request(method="POST", path="/a", headers={}, body=b"")
    req3 = Request(method="GET", path="/b", headers={}, body=b"")

    history = RequestHistory([req1, req2, req3])

    assert len(history.find(method="GET")) == 2
    assert len(history.find(path="/a")) == 2
    assert len(history.find(method="GET", path="/a")) == 1
    assert history.find(method="GET", path="/a")[0] == req1

def test_history_assertions():
    req = Request(method="GET", path="/test", headers={"x-id": "123"}, body=b"data")
    history = RequestHistory([req])

    # Should not raise
    history.assert_called()
    history.assert_called(count=1)
    history.assert_called(method="GET", path="/test")
    history.assert_called_with(method="GET", path="/test", body=b"data", headers={"X-ID": "123"})

    # Should raise
    with pytest.raises(AssertionError):
        history.assert_called(count=2)
    with pytest.raises(AssertionError):
        history.assert_called_with(method="POST", path="/test")
    with pytest.raises(AssertionError):
        history.assert_called_with(method="GET", path="/wrong")
    with pytest.raises(AssertionError):
        history.assert_called_with(method="GET", path="/test", body=b"wrong")
    with pytest.raises(AssertionError):
        history.assert_called_with(method="GET", path="/test", headers={"X-ID": "wrong"})
