import pytest
from websocket_server.frame import encode_frame, decode_frame, Opcode, FrameError, IncompleteFrameError

def test_encode_decode_small_text():
    text = "Hello, WebSocket!"
    encoded = encode_frame(Opcode.TEXT, text)
    frame, consumed = decode_frame(encoded)
    assert frame.opcode == Opcode.TEXT
    assert frame.payload == text
    assert frame.fin is True
    assert frame.mask is False
    assert consumed == len(encoded)

def test_encode_decode_binary():
    data = b"\x01\x02\x03\x04"
    encoded = encode_frame(Opcode.BINARY, data)
    frame, consumed = decode_frame(encoded)
    assert frame.opcode == Opcode.BINARY
    assert frame.payload == data
    assert frame.fin is True
    assert frame.mask is False
    assert consumed == len(encoded)

def test_encode_decode_with_masking():
    text = "Secret message"
    # Masking is usually done by clients, but our encoder supports it
    encoded = encode_frame(Opcode.TEXT, text, mask=True)
    frame, consumed = decode_frame(encoded)
    assert frame.opcode == Opcode.TEXT
    assert frame.payload == text
    assert frame.mask is True
    assert consumed == len(encoded)

def test_decode_extended_payload_2bytes():
    payload = b"A" * 200
    encoded = encode_frame(Opcode.BINARY, payload)
    assert encoded[1] == 126
    frame, consumed = decode_frame(encoded)
    assert frame.payload == payload
    assert consumed == len(encoded)

def test_decode_extended_payload_8bytes():
    payload = b"B" * 70000
    encoded = encode_frame(Opcode.BINARY, payload)
    assert encoded[1] == 127
    frame, consumed = decode_frame(encoded)
    assert frame.payload == payload
    assert consumed == len(encoded)

def test_decode_fragmented_data():
    text = "Part 1"
    encoded = encode_frame(Opcode.TEXT, text)
    # Give only part of the frame
    with pytest.raises(IncompleteFrameError, match="Incomplete payload"):
        decode_frame(encoded[:-2])

def test_decode_invalid_opcode():
    # Opcode 3 is reserved
    data = bytes([0x83, 0x00])
    with pytest.raises(FrameError, match="Unknown opcode: 3"):
        decode_frame(data)

def test_decode_short_frame():
    with pytest.raises(IncompleteFrameError, match="Frame too short"):
        decode_frame(b"\x81")

def test_decode_invalid_utf8_text_frame():
    # Opcode TEXT but invalid UTF-8 payload
    data = bytes([0x81, 0x02, 0xFF, 0xFF])
    with pytest.raises(FrameError, match="Invalid UTF-8 in text frame"):
        decode_frame(data)
