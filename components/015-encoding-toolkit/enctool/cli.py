import argparse
import sys
from typing import List, Optional

from .base64_tool import base64_decode, base64_encode
from .crc32_tool import calculate_crc32
from .encoding_tool import convert_encoding, detect_encoding
from .hash_tool import calculate_file_hash, calculate_hash, calculate_hmac
from .hex_tool import hex_decode, hex_encode
from .rot13_tool import rot13
from .url_tool import url_decode, url_encode


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments.

    Returns:
        The exit code.

    """
    parser = argparse.ArgumentParser(description="Encoding & Hash Toolkit")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Base64
    b64_parser = subparsers.add_parser("base64", help="Base64 commands")
    b64_subparsers = b64_parser.add_subparsers(
        dest="subcommand", help="Base64 subcommand"
    )
    b64_encode_parser = b64_subparsers.add_parser("encode", help="Base64 encode")
    b64_encode_parser.add_argument("data", help="Data to encode")
    b64_encode_parser.add_argument(
        "--url-safe", action="store_true", help="Use URL-safe encoding"
    )

    b64_decode_parser = b64_subparsers.add_parser("decode", help="Base64 decode")
    b64_decode_parser.add_argument("data", help="Data to decode")
    b64_decode_parser.add_argument(
        "--url-safe", action="store_true", help="Use URL-safe decoding"
    )

    # URL
    url_parser = subparsers.add_parser("url", help="URL commands")
    url_subparsers = url_parser.add_subparsers(dest="subcommand", help="URL subcommand")
    url_encode_parser = url_subparsers.add_parser("encode", help="URL encode")
    url_encode_parser.add_argument("data", help="Data to encode")

    url_decode_parser = url_subparsers.add_parser("decode", help="URL decode")
    url_decode_parser.add_argument("data", help="Data to decode")

    # Hex
    hex_parser = subparsers.add_parser("hex", help="Hex commands")
    hex_subparsers = hex_parser.add_subparsers(dest="subcommand", help="Hex subcommand")
    hex_encode_parser = hex_subparsers.add_parser("encode", help="Hex encode")
    hex_encode_parser.add_argument("data", help="Data to encode")

    hex_decode_parser = hex_subparsers.add_parser("decode", help="Hex decode")
    hex_decode_parser.add_argument("data", help="Data to decode")

    # ROT13
    rot13_parser = subparsers.add_parser("rot13", help="ROT13 transformation")
    rot13_parser.add_argument("data", help="Data to transform")

    # Hash
    hash_parser = subparsers.add_parser("hash", help="Hash commands")
    hash_parser.add_argument(
        "algorithm", choices=["md5", "sha1", "sha256"], help="Hashing algorithm"
    )
    hash_parser.add_argument("data", help="Data or file path to hash")
    hash_parser.add_argument(
        "--file", action="store_true", help="Treat data as a file path"
    )

    # HMAC
    hmac_parser = subparsers.add_parser("hmac", help="HMAC calculation")
    hmac_parser.add_argument(
        "algorithm", choices=["md5", "sha1", "sha256"], help="Hashing algorithm"
    )
    hmac_parser.add_argument("key", help="Secret key")
    hmac_parser.add_argument("data", help="Data to hash")

    # CRC32
    crc32_parser = subparsers.add_parser("crc32", help="CRC32 calculation")
    crc32_parser.add_argument("data", help="Data to checksum")

    # Detect
    detect_parser = subparsers.add_parser("detect", help="Detect text encoding")
    detect_parser.add_argument("file", help="File to detect encoding for")

    # Convert
    convert_parser = subparsers.add_parser("convert", help="Convert text encoding")
    convert_parser.add_argument("file", help="File to convert")
    convert_parser.add_argument("--from-enc", required=True, help="Source encoding")
    convert_parser.add_argument("--to-enc", required=True, help="Target encoding")

    args = parser.parse_args(argv)

    try:
        if args.command == "base64":
            if args.subcommand == "encode":
                print(base64_encode(args.data.encode("utf-8"), args.url_safe))
            elif args.subcommand == "decode":
                print(base64_decode(args.data, args.url_safe).decode("utf-8"))
            else:
                b64_parser.print_help()
                return 1
        elif args.command == "url":
            if args.subcommand == "encode":
                print(url_encode(args.data))
            elif args.subcommand == "decode":
                print(url_decode(args.data))
            else:
                url_parser.print_help()
                return 1
        elif args.command == "hex":
            if args.subcommand == "encode":
                print(hex_encode(args.data.encode("utf-8")))
            elif args.subcommand == "decode":
                print(hex_decode(args.data).decode("utf-8"))
            else:
                hex_parser.print_help()
                return 1
        elif args.command == "rot13":
            print(rot13(args.data))
        elif args.command == "hash":
            if args.file:
                with open(args.data, "rb") as f:
                    print(calculate_file_hash(f, args.algorithm))
            else:
                print(calculate_hash(args.data.encode("utf-8"), args.algorithm))
        elif args.command == "hmac":
            print(
                calculate_hmac(
                    args.key.encode("utf-8"), args.data.encode("utf-8"), args.algorithm
                )
            )
        elif args.command == "crc32":
            print(calculate_crc32(args.data.encode("utf-8")))
        elif args.command == "detect":
            with open(args.file, "rb") as f:
                data = f.read()
                result = detect_encoding(data)
                print(result if result else "Unknown")
        elif args.command == "convert":
            with open(args.file, "rb") as f:
                data = f.read()
            converted = convert_encoding(data, args.from_enc, args.to_enc)
            sys.stdout.buffer.write(converted)
            sys.stdout.flush()
        else:
            parser.print_help()
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0
