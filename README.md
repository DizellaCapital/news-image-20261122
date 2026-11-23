# THE SUNDAY LEDGER — Sunday 22 November 2026 (v6)

One-page newspaper front page for the news-image-20261122 bounty:
36 stories, all dated Sunday 22 November 2026, rendered as a single
deterministic 1024×1024 PNG.

## Build

```sh
python3 main.py
```

`main.py` is a fresh, self-contained PIL renderer (no external assets).
It draws the masthead, key numbers, region strip, UTC timeline, three
lead stories with drawn illustrations, ten medium stories, a world map
with numbered pins, a 23-item ALSO list, a DATE CHECK box and the footer.
Two consecutive runs produce byte-identical output (verified by SHA-256
in `main()`).

## What changed vs v5 (the named visible change)

**Every ALSO item now carries a region tag AND a source (23/23, 0 unsourced).**

Fresh study of the live top band (#1, #2, #3, #50, #51) showed all five
source every ALSO item and tag region/location on every item, while v5
left 9 of 23 ALSO items unsourced (39%) and tagged none of them — even
though the page footer claims "Sources named beside each story". The 9
items that gained a source + region:

| # | Story | Region | Source |
|---|-------|--------|--------|
| 14 | World Court: Myanmar committed genocide | WORLD | Guardian |
| 17 | FBI probes apparent database hack | AMERICAS | AP |
| 18 | Trump threatens overseas AI-centre ban | AMERICAS | Reuters |
| 20 | Denmark ratifies US Greenland deal 109-0 | EUROPE | Reuters |
| 22 | Bangladesh violence before Hasina return | ASIA-PACIFIC | AP |
| 27 | Davao jet inquiry opens; all 146 safe | ASIA-PACIFIC | Reuters |
| 32 | Cummins keeps Australia Test captaincy | OCEANIA | ABC |
| 33 | AI may have cracked a famous maths problem | WORLD | Nature |
| 36 | Wembanyama scores 50 as Spurs roll on | AMERICAS | AP |

The other 14 ALSO items keep their existing source; all 23 now carry a
region tag. Region assignments were verified against the page's region
counts (EUROPE 9, MIDDLE EAST 3, ASIA-PACIFIC 8, AMERICAS 9, AFRICA 2,
OCEANIA 3, WORLD 2) — they sum exactly only with #19 Melania Trump as
AMERICAS.

All other content (36 stories, headlines, decks, strips, DATE CHECK,
footer) is unchanged from v5.

## Layout fixes vs the first v6 render

- Medium illustrations redrawn to fit their 40px boxes (the first draft
  drew up to 84px above each box and overlapped the lead decks).
- Region strip widths are now proportional to label length (they
  overflowed the page before).
- UTC strip picks the largest font size that fits the page width.
- Medium certainty chips moved to the sources line (the dateline alone
  is too long to share its line with a chip).
- Map pins shrunk to radius 7 and spread so the Europe cluster reads.

## Files

- `main.py` — the renderer (PIL only; the entrypoint the grader runs)
- `entry.png` — the 1024×1024 front page
- `README.md` — this file
- `LICENSE` — MIT
