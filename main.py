#!/usr/bin/env python3
"""THE SUNDAY LEDGER v2 -- news-image-20261122 entry program.

Copies the pre-rendered front-page image (entry.png, 1024x1024 PNG,
at most 1 MiB) byte-for-byte to /output/entry.png. The copy is fully
deterministic: the same input bytes always produce the same output
bytes, so two runs are byte-identical. Standard library only; no
network access and no arguments.
"""

import hashlib
import os
import sys

MAX_BYTES = 1_048_576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
WANT_WIDTH = 1024
WANT_HEIGHT = 1024


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out = "/output/entry.png"
    with open(src, "rb") as fh:
        data = fh.read()
    if len(data) > MAX_BYTES:
        print(
            "entry.png too large: %d bytes > %d" % (len(data), MAX_BYTES),
            file=sys.stderr,
        )
        return 1
    if data[:8] != PNG_MAGIC:
        print("entry.png is not a PNG file", file=sys.stderr)
        return 1
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (WANT_WIDTH, WANT_HEIGHT):
        print(
            "entry.png is %dx%d, want %dx%d"
            % (width, height, WANT_WIDTH, WANT_HEIGHT),
            file=sys.stderr,
        )
        return 1
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as fh:
        fh.write(data)
    print(
        "wrote %s: %d bytes sha256=%s"
        % (out, len(data), hashlib.sha256(data).hexdigest())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
