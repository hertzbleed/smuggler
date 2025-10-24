#!/usr/bin/env python3
"""Create an HTML file that embeds any file in base64 format based on a template/default.html ."""

import base64
import sys
from pathlib import Path
from typing import Optional

DEFAULT_TEMPLATE_NAME = "default.html"

def build_smuggled_html(source_path: Path, template_path: Path, dest_path: Path) -> None:
    """Embed the binary contents of source_path into template_path and write dest_path."""
    if not source_path.exists() or not source_path.is_file():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    if not template_path.exists() or not template_path.is_file():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    #base64-encode it the source file
    with source_path.open("rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")

    #Reading template and replacing placeholders...
    with template_path.open("r", encoding="utf-8") as t:
        template_text = t.read()

    output_text = template_text.replace("BASE64GOESHERE", encoded)
    output_text = output_text.replace("STATIC FILE NAME", source_path.name)

    #Write the resulting HTML 
    with dest_path.open("w", encoding="utf-8") as out:
        out.write(output_text)

    print(f"Success! Created: {dest_path}")


def parse_args(args: list) -> tuple[Path, Path, Path]:
    """
    Acceptable usages:
      python html_smuggler.py <file-to-smuggle>
      python html_smuggler.py <file-to-smuggle> --template=default.html
    """
    if not args:
        raise SystemExit("Usage: python html_smuggler.py <file-to-smuggle> [--template=path] [--out=path]")

    src = Path(args[0])
    template = Path(DEFAULT_TEMPLATE_NAME)
    out = src.with_suffix(".html")

    for token in args[1:]:
        if token.startswith("--template="):
            template = Path(token.split("=", 1)[1])
        elif token.startswith("--out="):
            out = Path(token.split("=", 1)[1])
        else:
            raise SystemExit(f"Unrecognized option: {token}")

    return src, template, out


def main() -> None:
    try:
        src_path, tpl_path, out_path = parse_args(sys.argv[1:])
        build_smuggled_html(src_path, tpl_path, out_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
