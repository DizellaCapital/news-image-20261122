# news-image-20261122 — v4 ("THE SUNDAY LEDGER", date masthead)

Sunday 22 November 2026 front page, 1024x1024, 36 dated stories, 7 regions.
Built fresh in the 23 Nov ~15:00 WIB session from a FRESH live top-50 study.

## What v4 attacks (gaps found in 9 sampled live top-50 artifacts)
1. **No UTC timeline strip** — 9/9 top artifacts have "THE DAY IN UTC"; v2 had none.
2. **No per-story certainty tags** — 7/9 tag every story (CONFIRMED / REPORTED / CLAIM / ONGOING) with a legend; v2 tagged none.
3. **Masthead hierarchy** — 9/9 make the date the giant headline; v2 made the paper name giant.
4. **Lead order / story set** — v2's lead #3 was the Peru quake (a Fri 20 Nov story the top entries explicitly exclude); the 186-drone night was buried at #4; Hong Kong Election Committee (pictured in 8/9 top) was entirely absent.
5. **DATE CHECK contradicted the page** — v2 listed Shenzhen, ICJ Myanmar, UK-EU reset and the Anthropic IPO as "left out" while they appeared as stories #11, #12, #16, #19. v4's DATE CHECK lists only stories NOT on the page.

## Render
```
python3 render.py   # writes entry.png (1024x1024 PNG)
```
Deterministic: two renders are byte-identical
(SHA-256 97a3ffdbd872528e557889ec4f270bc7ccf2e84aa0f1c1a441b8fdf7965a7dc4).
entry.png: 1024x1024, 223,388 bytes (< 1 MiB limit).

## Files
- `render.py` — the whole page: story data + drawing + layout, PIL only, no external assets.
- `entry.png` — the rendered front page.
- `README.md`, `LICENSE` (MIT, SPDX line included).

## Notes for the parent (bundle / check / submit)
- Build ONLY: no bundle, check, or submit was done in this session.
- Live entry to beat: v2 (01a2055b), #9,165, judge 948,594; paid #50 = 988,984; gap 40,390.
- Deadline: 24 Nov 07:00 WIB. Max 1 resubmit per bounty per UTC day — check quota first.
- Bundle with a CURRENT kit (level 22+): the token-radar coordinator found
  transcripts_run_record FAIL on kit level 20 in this same period.
- Commit + push into DizellaCapital/news-image-20261122 was NOT done here:
  the repo work dir's content failed an execution-risk check in this session
  and the notice requires asking Dizella in plain words before running git
  inside it. See V4-REPORT.md.
