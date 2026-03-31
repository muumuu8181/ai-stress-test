import pytest
from src.canvas import Canvas


def test_canvas_init():
    width, height = 50, 50
    canvas = Canvas(width, height, (0, 0, 0))
    assert canvas.width == width
    assert canvas.height == height
    assert len(canvas.pixels) == width * height * 3
    # Check background color (black)
    assert canvas.pixels[0:3] == bytearray([0, 0, 0])
    assert canvas.pixels[-3:] == bytearray([0, 0, 0])


def test_canvas_init_invalid():
    with pytest.raises(ValueError, match="width and height must be positive"):
        Canvas(0, 100)
    with pytest.raises(ValueError, match="width and height must be positive"):
        Canvas(100, -1)


def test_set_pixel():
    canvas = Canvas(10, 10, (255, 255, 255))
    color = (255, 0, 0)
    canvas.set_pixel(1, 1, color)
    index = (1 * 10 + 1) * 3
    assert canvas.pixels[index : index + 3] == bytearray(color)


def test_set_pixel_out_of_bounds():
    canvas = Canvas(10, 10, (255, 255, 255))
    initial_pixels = bytes(canvas.pixels)
    canvas.set_pixel(-1, 0, (0, 0, 0))
    canvas.set_pixel(10, 0, (0, 0, 0))
    canvas.set_pixel(0, -1, (0, 0, 0))
    canvas.set_pixel(0, 10, (0, 0, 0))
    # Should not change anything
    assert bytes(canvas.pixels) == initial_pixels


def test_draw_rect_outline():
    canvas = Canvas(10, 10, (255, 255, 255))
    color = (0, 255, 0)
    canvas.draw_rect(2, 2, 4, 4, color, fill=False)

    # Check top-left
    index = (2 * 10 + 2) * 3
    assert canvas.pixels[index : index + 3] == bytearray(color)
    # Check bottom-right
    index = (5 * 10 + 5) * 3
    assert canvas.pixels[index : index + 3] == bytearray(color)
    # Check center (should be white)
    index = (3 * 10 + 3) * 3
    assert canvas.pixels[index : index + 3] == bytearray([255, 255, 255])


def test_draw_rect_fill():
    canvas = Canvas(10, 10, (255, 255, 255))
    color = (0, 0, 255)
    canvas.draw_rect(2, 2, 4, 4, color, fill=True)

    # Check top-left
    index = (2 * 10 + 2) * 3
    assert canvas.pixels[index : index + 3] == bytearray(color)
    # Check center (should be blue now)
    index = (3 * 10 + 3) * 3
    assert canvas.pixels[index : index + 3] == bytearray(color)


def test_draw_line():
    canvas = Canvas(10, 10, (255, 255, 255))
    color = (0, 0, 0)
    canvas.draw_line(0, 0, 5, 5, color)

    # Check some points on the line
    for i in range(6):
        index = (i * 10 + i) * 3
        assert canvas.pixels[index : index + 3] == bytearray(color)


def test_clear():
    canvas = Canvas(10, 10, (255, 255, 255))
    canvas.set_pixel(0, 0, (0, 0, 0))
    canvas.clear((128, 128, 128))
    assert canvas.pixels[0:3] == bytearray([128, 128, 128])


def test_to_png_integration():
    canvas = Canvas(10, 10, (255, 255, 255))
    canvas.draw_rect(0, 0, 10, 10, (255, 0, 0), fill=True)
    png_bytes = canvas.to_png()

    assert isinstance(png_bytes, bytes)
    assert png_bytes.startswith(b"\x89PNG")
    assert b"IHDR" in png_bytes
    assert b"IDAT" in png_bytes
    assert b"IEND" in png_bytes
