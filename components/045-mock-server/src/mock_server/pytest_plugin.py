import pytest
from .server import MockServer

@pytest.fixture
def mock_server():
    """Pytest fixture providing a started MockServer instance."""
    with MockServer() as server:
        yield server
