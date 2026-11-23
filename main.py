#!/usr/bin/env python3
"""THE SUNDAY LEDGER v7 -- news-image-20261122 entry program.

Copies the pre-rendered front page (entry.png, 1024x1024 PNG, at most
1 MiB) byte-for-byte to the output directory the grader provides
(MAKEFUN_OUTPUT_DIR, /output in the graded run). Standard library
only: the graded container installs nothing, so this program imports
nothing beyond the stdlib and never draws anything itself. The image
is drawn by render.py in this same directory (PIL, run locally); this
program only validates the bytes and copies them.

One named change vs v6-fix: the COP31 lead is corrected -- the final
text landed on Sunday morning (headline + deck + kicker + UTC strip),
the Iran lead deck names Al-Riffa and Awali, the DATE CHECK drops the
uncorroborated Antarctic IPO item, and the world map is a recognisable
dotted world map.
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
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not os.path.isdir(out_dir):
        out_dir = here
    out = os.path.join(out_dir, "entry.png")
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
    os.makedirs(out_dir, exist_ok=True)
    with open(out, "wb") as fh:
        fh.write(data)
    print(
        "wrote %s: %d bytes sha256=%s"
        % (out, len(data), hashlib.sha256(data).hexdigest())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
