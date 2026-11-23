#!/usr/bin/env python3
"""THE SUNDAY LEDGER v6 -- news-image-20261122 entry program.

Copies the pre-rendered front page (entry.png, 1024x1024 PNG, at most
1 MiB) byte-for-byte to the output directory the grader provides
(MAKEFUN_OUTPUT_DIR, /output in the graded run). Standard library
only: the graded container installs nothing, so this program imports
nothing beyond the stdlib and never draws anything itself. The image
is drawn by render.py in this same directory (PIL, run locally); this
program only validates the bytes and copies them.

One named change vs v5: every one of the 23 ALSO items now carries a
REGION tag AND a source (0 unsourced, 23/23 region-tagged).
"""

import hashlib
import os
import sys

MAX_BYTES = 1_048_576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
WANT_WIDTH = 1024
WANT_HEIGHT = 1024


def output_dir(here):
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        return env
    if os.path.isdir("/output"):
        return "/output"
    return here


def fail(message):
    print(message, file=sys.stderr)
    return 1


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = output_dir(here)
    out = os.path.join(out_dir, "entry.png")
    try:
        with open(src, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        return fail("cannot read entry.png: %s" % exc)
    if len(data) > MAX_BYTES:
        return fail(
            "entry.png too large: %d bytes > %d" % (len(data), MAX_BYTES)
        )
    if data[:8] != PNG_MAGIC:
        return fail("entry.png is not a PNG file")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (WANT_WIDTH, WANT_HEIGHT):
        return fail(
            "entry.png is %dx%d, want %dx%d"
            % (width, height, WANT_WIDTH, WANT_HEIGHT)
        )
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(out, "wb") as fh:
            fh.write(data)
    except OSError as exc:
        return fail("cannot write %s: %s" % (out, exc))
    print(
        "wrote %s: %d bytes sha256=%s"
        % (out, len(data), hashlib.sha256(data).hexdigest())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
