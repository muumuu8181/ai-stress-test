import argparse
import json
import os
import sys
try:
    from .parser import MailParser # type: ignore
except ImportError:
    from parser import MailParser # type: ignore

def main() -> None:
    """
    Main entry point for the mail-parser CLI.
    """
    parser = argparse.ArgumentParser(description="Parse MIME email files.")
    parser.add_argument("input", help="Path to the raw email file (or '-' for stdin).")
    parser.add_argument("-o", "--output", help="Output file (JSON format). If not specified, prints to stdout.")
    parser.add_argument("-a", "--attachments", help="Directory to save attachments.")

    args = parser.parse_args()

    try:
        if args.input == '-':
            raw_email = sys.stdin.buffer.read()
        else:
            with open(args.input, 'rb') as f:
                raw_email = f.read()

        mail = MailParser.parse(raw_email)

        result = {
            "subject": mail.subject,
            "from": mail.from_address,
            "to": mail.to_addresses,
            "date": mail.date,
            "headers": mail.headers,
            "content": {
                "text": mail.content.text,
                "html": mail.content.html
            },
            "attachments": [
                {
                    "filename": att.filename,
                    "content_type": att.content_type,
                    "size": len(att.content),
                    "content_id": att.content_id
                }
                for att in mail.attachments
            ]
        }

        if args.attachments:
            os.makedirs(args.attachments, exist_ok=True)
            for att in mail.attachments:
                filename = att.filename or "unnamed"
                # Basic sanitization for filename
                filename = "".join(c for c in filename if c.isalnum() or c in ('.', '_', '-')).strip()
                if not filename:
                    filename = "unnamed"

                path = os.path.join(args.attachments, filename)
                with open(path, 'wb') as f:
                    f.write(att.content)
                print(f"Saved attachment: {path}", file=sys.stderr)

        output_json = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_json)
        else:
            print(output_json)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
