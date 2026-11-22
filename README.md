[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/DizellaCapital/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/DizellaCapital/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# THE SUNDAY LEDGER — Sunday 22 November 2026 (v2)

A rebuilt one-page broadsheet front page for 22 November 2026: **36 dated
stories, 7 regions, 13 illustrated cards** — COP31 deadlock deep into
Sunday (zero fossil-fuel mentions in the draft), Gulf tankers hit off Oman
and in the Strait of Hormuz with one crew member missing, the Peru quake
revised to M6.9, Kyiv bridges struck, the Baltic cargo-ship drone hit,
Estonia closing its Russia border, Verstappen inheriting the Las Vegas
pole, Rahul 124 not out in Wellington, the Sinaloa cartel crackdown,
Bolsonaro in ICU, the Shenzhen three-way declaration, the ICJ Myanmar
genocide verdict, and Australia ending England's T20 streak.

v2 is a full visual rebuild of the front page: redrawn hero scenes with
opaque caption strips (COP31 plenary dome and overtime clock, the Hormuz
tanker, the Andes seismic chart), a new numbers strip, a region bar, ten
framed vignettes, a world map with numbered pins and leader lines for the
close European pins, numbered briefs 14–36, and a date-check footer naming
the big Wednesday–Friday stories deliberately left out.

## How it is built

- `entry.png` is the whole 1024×1024 front page, rendered fresh for v2
  (masthead, stat strip, region bar, 3 hero scenes, 10 vignettes, world
  map with pins 1–13, briefs 14–36, date-check footer).
- `main.py` (Python 3.13, standard library only) copies `entry.png`
  byte-for-byte to `/output/entry.png`, validating the PNG magic bytes,
  the 1024×1024 dimensions, and the 1 MiB size cap. That is the entry the
  judge sees. Two runs produce byte-identical output.

```sh
python3 main.py   # -> /output/entry.png (1024x1024 PNG)
```

## Sources

All 36 stories verified 22 November 2026 via live web search: Reuters, AP,
AFP, BBC, IAEA, ICJ, Formula1.com, CAAP, PTI, ABC, Health Policy Watch,
Carbon Brief, Kyiv Independent, Times of India, Peru Geophysical Institute,
NDTV, Cricket Australia.
