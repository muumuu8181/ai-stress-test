# PNG Image Writer from Scratch

A simple Python library to generate PNG images from scratch using only the `struct` and `zlib` modules.

## Features

- Core PNG generation with IHDR, IDAT, and IEND chunks.
- Simple Canvas API for drawing shapes.
- Basic drawing primitives: `set_pixel`, `draw_rect`, `draw_line`.
- Type hints and docstrings for all public APIs.

## Installation

No external dependencies required other than Python 3.

## Usage

### Simple Drawing Example

```python
from src.canvas import Canvas

# Create a 100x100 canvas with a white background
canvas = Canvas(100, 100, (255, 255, 255))

# Draw a red rectangle (outline)
canvas.draw_rect(10, 10, 80, 80, (255, 0, 0))

# Draw a blue filled rectangle
canvas.draw_rect(30, 30, 40, 40, (0, 0, 255), fill=True)

# Draw a green line
canvas.draw_line(0, 0, 99, 99, (0, 255, 0))

# Export to PNG and save to a file
png_bytes = canvas.to_png()
with open("output.png", "wb") as f:
    f.write(png_bytes)
```

## API Reference

### `Canvas`

- `__init__(width: int, height: int, background_color: Tuple[int, int, int] = (255, 255, 255))`
- `clear(color: Tuple[int, int, int])`: Clears the canvas with the specified color.
- `set_pixel(x: int, y: int, color: Tuple[int, int, int])`: Sets the color of a single pixel.
- `draw_rect(x, y, width, height, color, fill=False)`: Draws a rectangle.
- `draw_line(x1, y1, x2, y2, color)`: Draws a line using Bresenham's algorithm.
- `to_png() -> bytes`: Returns the PNG byte stream of the current canvas.

## CLI Usage

Generate a demo image:

```bash
cd components/033-png-writer
PYTHONPATH=. python3 src/cli.py --demo --output demo.png
```

## Testing

Run tests using `pytest`:

```bash
cd components/033-png-writer
PYTHONPATH=. pytest --cov=src tests/
```
