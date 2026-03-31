import unittest.mock as mock
import socket
import pytest
from dnsclient.transport import query_udp, query_tcp, DNSTransportError


@mock.patch("socket.getaddrinfo")
@mock.patch("socket.socket")
def test_query_udp_ipv6(mock_socket, mock_getaddrinfo):
    # Mock IPv6 addrinfo
    mock_getaddrinfo.return_value = [
        (socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP, "", ("::1", 53, 0, 0))
    ]

    mock_instance = mock_socket.return_value.__enter__.return_value
    mock_instance.recvfrom.return_value = (b"resp", ("::1", 53))

    query_udp(b"query", "::1")

    # Check socket was created with AF_INET6
    mock_socket.assert_called_with(socket.AF_INET6, socket.SOCK_DGRAM)
    # Check sendto used IPv6 sockaddr
    mock_instance.sendto.assert_called_with(b"query", ("::1", 53, 0, 0))


@mock.patch("socket.getaddrinfo")
@mock.patch("socket.socket")
def test_query_tcp_ipv6(mock_socket, mock_getaddrinfo):
    # Mock IPv6 addrinfo
    mock_getaddrinfo.return_value = [
        (socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("::1", 53, 0, 0))
    ]

    mock_instance = mock_socket.return_value.__enter__.return_value
    # TCP resp: 2 bytes length (4) + "resp"
    mock_instance.recv.side_effect = [b"\x00\x04", b"resp"]

    query_tcp(b"query", "::1")

    mock_socket.assert_called_with(socket.AF_INET6, socket.SOCK_STREAM)
    mock_instance.connect.assert_called_with(("::1", 53, 0, 0))
