# Sunday 22 November 2026 — one-page newspaper (v5)

A single 1024x1024 front page: 36 stories, 7 regions, every one dated
Sunday 22 November 2026. All scenes are drawn illustrations of reported
events, not photographs. Sources are named beside each story.

## What v5 changes (visible in the first 5 seconds)
- **Every displayed deck is a complete sentence.** v4 clipped 8 of 13 decks
  mid-sentence (lead #1 ended on "and", lead #3 on "no", mediums on
  "Moscow" / "turnout" / "New Zealand's" ...). v5's renderer measures every
  deck and refuses to render a cut sentence: 0 truncated decks of 13.
- **Cricket story aligned to the key number:** "India declare on a record
  720/9" (Rahul 136, Pant 128). v4's story said "India 344 for 2" while the
  key strip said 720/9.
- **DATE CHECK fix:** "Bayelsa boat capsize" (v4 wrote "Bahrain boat capsize").

Kept from v4: giant-date masthead, UTC strip (7 events), per-story certainty
tags + legend, lead order (COP31, 186 drones, Bahrain), the 36-story set.

## Build
```sh
python3 render.py entry.png
```
Pure PIL, no external assets, no network, no clock: two runs produce a
byte-identical PNG (SHA-256 printed by the script). `render.py` asserts at
build time that every deck fits its box whole and ends with terminal
punctuation, that no headline wraps past 2 lines, and that the page ends
inside 1024 px — a violation fails the build instead of shipping a cut deck.

## Files
- `render.py` — the whole page: story data + deck-fitting engine + drawing.
- `entry.png` — the 1024x1024 front page (deterministic).
- `README.md` — this file.
- `LICENSE` — MIT.
