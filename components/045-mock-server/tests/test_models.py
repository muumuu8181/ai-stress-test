import pytest
from mock_server.models import Request, Response, Rule

def test_request_initialization():
    req = Request(method="GET", path="/test", headers={"X-Test": "1"}, body=b"hello", query={"a": ["1"]})
    assert req.method == "GET"
    assert req.path == "/test"
    assert req.headers["X-Test"] == "1"
    assert req.body == b"hello"
    assert req.query == {"a": ["1"]}

def test_response_get_body_bytes():
    resp_str = Response(body="hello")
    assert resp_str.get_body_bytes() == b"hello"

    resp_bytes = Response(body=b"world")
    assert resp_bytes.get_body_bytes() == b"world"

def test_rule_matching():
    matcher = lambda r: r.path == "/match"
    rule = Rule(matcher=matcher, response_generator=lambda r: Response(status=200))

    req_match = Request(method="GET", path="/match", headers={}, body=b"")
    req_no_match = Request(method="GET", path="/no-match", headers={}, body=b"")

    assert rule.matches(req_match) is True
    assert rule.matches(req_no_match) is False

def test_sequential_rule():
    responses = [Response(status=201), Response(status=202)]
    rule = Rule(
        matcher=lambda r: True,
        response_generator=lambda r: Response(status=500),
        is_sequential=True,
        responses=responses
    )

    req = Request(method="GET", path="/", headers={}, body=b"")

    assert rule.get_response(req).status == 201
    assert rule.get_response(req).status == 202
    assert rule.get_response(req).status == 202  # Stays at last response
