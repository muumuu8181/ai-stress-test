from typing import Tuple
from .png_writer import generate_png


class Canvas:
    """
    A simple canvas for drawing shapes and exporting to PNG.
    """

    def __init__(
        self,
        width: int,
        height: int,
        background_color: Tuple[int, int, int] = (255, 255, 255),
    ):
        """
        Initializes the canvas.

        Args:
            width: Image width in pixels.
            height: Image height in pixels.
            background_color: Initial background color as an (R, G, B) tuple.
        """
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")

        self.width = width
        self.height = height
        # Initialize pixel buffer (flat bytearray for performance)
        self.pixels = bytearray(width * height * 3)
        self.clear(background_color)

    def clear(self, color: Tuple[int, int, int]):
        """
        Clears the canvas with the specified color.

        Args:
            color: The color to clear the canvas with as an (R, G, B) tuple.
        """
        r, g, b = color
        for i in range(0, len(self.pixels), 3):
            self.pixels[i] = r
            self.pixels[i + 1] = g
            self.pixels[i + 2] = b

    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]):
        """
        Sets the color of a single pixel.

        Args:
            x: X-coordinate of the pixel.
            y: Y-coordinate of the pixel.
            color: The color as an (R, G, B) tuple.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            index = (y * self.width + x) * 3
            self.pixels[index] = color[0]
            self.pixels[index + 1] = color[1]
            self.pixels[index + 2] = color[2]

    def draw_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int],
        fill: bool = False,
    ):
        """
        Draws a rectangle on the canvas.

        Args:
            x: X-coordinate of the top-left corner.
            y: Y-coordinate of the top-left corner.
            width: Width of the rectangle.
            height: Height of the rectangle.
            color: The color as an (R, G, B) tuple.
            fill: Whether to fill the rectangle with the color.
        """
        if fill:
            for dy in range(height):
                for dx in range(width):
                    self.set_pixel(x + dx, y + dy, color)
        else:
            # Draw top and bottom sides
            for dx in range(width):
                self.set_pixel(x + dx, y, color)
                self.set_pixel(x + dx, y + height - 1, color)
            # Draw left and right sides
            for dy in range(height):
                self.set_pixel(x, y + dy, color)
                self.set_pixel(x + width - 1, y + dy, color)

    def draw_line(
        self, x1: int, y1: int, x2: int, y2: int, color: Tuple[int, int, int]
    ):
        """
        Draws a line using Bresenham's algorithm.

        Args:
            x1, y1: Starting coordinates.
            x2, y2: Ending coordinates.
            color: The color as an (R, G, B) tuple.
        """
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy

        while True:
            self.set_pixel(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy

    def to_png(self) -> bytes:
        """
        Exports the canvas to a PNG byte stream.

        Returns:
            The complete PNG byte stream.
        """
        return generate_png(self.width, self.height, bytes(self.pixels))
