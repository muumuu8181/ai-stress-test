import urllib.request
import pytest
from mock_server.models import Response

def test_pytest_fixture(mock_server):
    """Verifies that the mock_server fixture works and is pre-started."""
    mock_server.when("GET", "/fixture", response_body="FIXTURE_OK")

    url = f"{mock_server.url}/fixture"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        assert resp.read() == b"FIXTURE_OK"

def test_integration_post_json(mock_server):
    import json
    @mock_server.on("POST", "/json")
    def handle_json(req):
        data = json.loads(req.body.decode())
        return Response(body=json.dumps({"received": data["value"]}).encode())

    url = f"{mock_server.url}/json"
    req_body = json.dumps({"value": 42}).encode()
    req = urllib.request.Request(url, data=req_body, method="POST", headers={"Content-Type": "application/json"})

    with urllib.request.urlopen(req) as resp:
        res_data = json.loads(resp.read().decode())
        assert res_data["received"] == 42

def test_integration_not_found(mock_server):
    """Verifies 404 behavior for unmatched requests."""
    url = f"{mock_server.url}/missing"
    with pytest.raises(urllib.error.HTTPError) as excinfo:
        urllib.request.urlopen(url)
    assert excinfo.value.code == 404

def test_integration_head_request(mock_server):
    mock_server.when("HEAD", "/head", status=200, response_headers={"X-Test": "123"}, response_body="This should not be returned")

    conn = urllib.request.urlopen(urllib.request.Request(f"{mock_server.url}/head", method="HEAD"))
    assert conn.status == 200
    assert conn.read() == b""
    assert conn.headers["X-Test"] == "123"

def test_integration_query_params(mock_server):
    mock_server.when("GET", "/query", response_body="OK")

    urllib.request.urlopen(f"{mock_server.url}/query?a=1&b=2&a=3")

    history = mock_server.get_history()
    last_req = history.last()
    assert last_req.query == {"a": ["1", "3"], "b": ["2"]}

    history.assert_called_with("GET", "/query", query={"a": ["1", "3"], "b": ["2"]})
