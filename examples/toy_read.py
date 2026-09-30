#!/usr/bin/env python3
"""Count lines and words in a text file and print a one-line summary.

Usage:
  toy_read.py --file notes.txt [--top N]

Reads TOY_DATA_DIR for a default directory when --file is relative.
Exit codes: 0 on success, 1 if the file is missing, 2 on bad arguments.
"""
import argparse
import os
import sys

DATA_DIR = os.environ.get("TOY_DATA_DIR", ".")


def main():
    ap = argparse.ArgumentParser(description="Summarize a text file.")
    ap.add_argument("--file", required=True, help="text file to summarize")
    ap.add_argument("--top", type=int, default=0, help="print first N lines as a preview")
    args = ap.parse_args()

    path = args.file if os.path.isabs(args.file) else os.path.join(DATA_DIR, args.file)
    if not os.path.isfile(path):
        print(f"toy_read: no such file: {path}", file=sys.stderr)
        return 1
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    lines = text.splitlines()
    words = text.split()
    print(f"{path}: {len(lines)} lines, {len(words)} words")
    for ln in lines[: args.top]:
        print("  | " + ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
