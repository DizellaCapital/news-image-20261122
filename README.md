# THE SUNDAY LEDGER — Koran 22 Nov v7

One-page front page summing up the world's news of Sunday 22 November 2026:
36 stories, 7 regions, every one dated Sunday 22 November 2026.

## Files

- `entry.png` — the front page, 1024×1024 PNG (deterministic: two renders
  byte-identical).
- `render.py` — the renderer (PIL, run locally only; never run by the
  grader). Draws every scene and label in code; no external assets.
- `main.py` — the entry program (stdlib only): validates `entry.png`
  (≤1 MiB, PNG magic, 1024×1024) and copies it to `MAKEFUN_OUTPUT_DIR`.

## Named change vs v6-fix

The COP31 lead is corrected: the final text LANDED on Sunday morning.
Headline, deck, kicker and UTC strip now say so (was: "deadlock deepens /
no deal"). The Iran lead deck names Al-Riffa and Awali. The DATE CHECK
drops the uncorroborated Antarctic IPO item. The world map is a
recognisable dotted world map. Everything else is identical to v6-fix
(same 36 stories, same decks except the two leads above, same ALSO list,
same footer).

## Render locally

```
python3 render.py   # writes entry.png, renders twice, checks byte-identical
```

## Run as the grader does

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```
