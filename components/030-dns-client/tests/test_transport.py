import socket
import struct
import unittest.mock as mock
import pytest
from dnsclient.transport import query_udp, query_tcp, send_query, DNSTransportError
from dnsclient.protocol import DNSPacket, DNSHeader, DNSQuestion, DNSType


@mock.patch("socket.socket")
def test_query_udp(mock_socket):
    mock_instance = mock_socket.return_value.__enter__.return_value
    mock_instance.recvfrom.return_value = (b"response_data", ("1.2.3.4", 53))

    response = query_udp(b"query_data", "1.2.3.4")
    assert response == b"response_data"
    mock_instance.sendto.assert_called_once_with(b"query_data", ("1.2.3.4", 53))


@mock.patch("socket.socket")
def test_query_tcp(mock_socket):
    mock_instance = mock_socket.return_value.__enter__.return_value

    # TCP response: 2-byte length + actual data
    data = b"response_data"
    length = len(data)
    mock_instance.recv.side_effect = [struct.pack("!H", length), data]

    response = query_tcp(b"query_data", "1.2.3.4")
    assert response == data
    mock_instance.connect.assert_called_once_with(("1.2.3.4", 53))
    mock_instance.sendall.assert_called_once_with(struct.pack("!H", 10) + b"query_data")


@mock.patch("socket.socket")
def test_query_udp_timeout(mock_socket):
    mock_instance = mock_socket.return_value.__enter__.return_value
    mock_instance.recvfrom.side_effect = socket.timeout

    with pytest.raises(DNSTransportError, match="timed out"):
        query_udp(b"query_data", "1.2.3.4")
