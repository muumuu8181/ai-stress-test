import argparse
from src.canvas import Canvas


def main():
    parser = argparse.ArgumentParser(description="A simple PNG image writer.")
    parser.add_argument("--width", type=int, default=200, help="Width of the image")
    parser.add_argument("--height", type=int, default=200, help="Height of the image")
    parser.add_argument("--output", type=str, default="output.png", help="Output PNG file path")
    parser.add_argument("--demo", action="store_true", help="Generate a demo image")

    args = parser.parse_args()

    canvas = Canvas(args.width, args.height)

    if args.demo:
        # Draw some shapes for demo
        # Red rectangle
        canvas.draw_rect(20, 20, args.width - 40, args.height - 40, (255, 0, 0))
        # Blue filled rectangle
        canvas.draw_rect(50, 50, args.width - 100, args.height - 100, (0, 0, 255), fill=True)
        # Green lines
        canvas.draw_line(0, 0, args.width - 1, args.height - 1, (0, 255, 0))
        canvas.draw_line(0, args.height - 1, args.width - 1, 0, (0, 255, 0))
        print(f"Generating demo image: {args.output}")

    png_bytes = canvas.to_png()
    with open(args.output, "wb") as f:
        f.write(png_bytes)

    if not args.demo:
        print(f"Generated empty {args.width}x{args.height} image: {args.output}")


if __name__ == "__main__":
    main()
