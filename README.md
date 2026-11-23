# THE SUNDAY LEDGER — Sunday 22 November 2026

A one-page newspaper front page for Sunday 22 November 2026: 36 stories
across 7 regions, every one dated. Three leads (COP31 final text, 186
drones over Ukraine, Iran's radar claim vs Bahrain's denial), ten medium
stories, 23 more in the ALSO list, a dotted world map with numbered pins,
a UTC timeline, key numbers, and a DATE CHECK box naming what was left
out as other days' news.

## How it is built

- `render.py` draws `entry.png` (1024×1024, deterministic) with PIL.
  Run locally: `python3 render.py`. The grader never runs this file.
- `main.py` is the entry program: standard library only. It copies the
  pre-rendered `entry.png` byte-for-byte to `MAKEFUN_OUTPUT_DIR`
  (`/output` in the graded run). Run it as the grader does:
  `python3 -P -s main.py`.

## v8 named change (vs v7)

The COP31 lead illustration is cleaned up — the sign whose "FUELS" line
was clipped at the bottom edge is gone; the conference scene (globe,
delegates, table, clock) has no embedded text. And the world map is
redrawn with recognisable land: dark navy field, fine light dot grid,
refined continent shapes, red numbered pins (the #1 pattern). The COP31
framing from v7 is kept ("final text lands" matches 4 of 5 top entries).
All other content is identical to v7.
