[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/DizellaCapital/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/DizellaCapital/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# THE SUNDAY LEDGER — Sunday 22 November 2026

A one-page broadsheet front page for 22 November 2026: **36 dated stories,
7 regions, 13 illustrated cards** — COP31 deadlock deep into Sunday, Gulf
tankers hit off Oman, Peru quake revised to M6.9, Kyiv bridges struck, the
Baltic cargo-ship drone hit, Estonia closing its Russia border, Verstappen
inheriting the Las Vegas pole, Rahul 124 not out in Wellington, the Sinaloa
cartel crackdown, Bolsonaro in ICU, the Shenzhen three-way declaration, the
ICJ Myanmar genocide verdict, and Australia ending England's T20 streak.
Warm newsprint, serif headlines, a "22 Nov by the numbers" strip, a dotted
world map with numbered pins for stories 1–13, and a date-check footer that
names the big Wednesday–Friday stories deliberately left out.

## How it is built

- `render.html` is the whole 1024×1024 front page (inline CSS + SVG
  illustrations + a small script that draws the dotted world map and pins
  from the stories' coordinates).
- `render.mjs` screenshots it with Playwright (Chromium) to `entry.png`.
- `main.ts` (Node 22, standard library only) copies `entry.png` to the
  output directory. That is the entry the judge sees.
- `stories_20261122.json` is the verified dataset behind the page: all 36
  stories, dated Sunday 22 November 2026, with region, dateline, source,
  and coordinates for the illustrated stories.

```sh
node render.mjs          # render.html -> entry.png (1024x1024)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # -> out/entry.png
```

## Sources

All 36 stories verified 22 November 2026 via live web search: Reuters, AP,
AFP, BBC, IAEA, ICJ, Formula1.com, CAAP, PTI, ABC, Health Policy Watch,
Carbon Brief, Kyiv Independent, Times of India, Peru Geophysical Institute,
NDTV, Cricket Australia.
