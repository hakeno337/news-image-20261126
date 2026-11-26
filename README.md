# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/hakeno337/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/hakeno337/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

One image that sums up the world's news of Thursday 26 November 2026, set as an illustrated broadsheet front page under a black date band: a nor'easter drenching Thanksgiving Day on the US East Coast, the US proposing a 15% tariff on Taiwan, and king tides flooding California's coast as the three drawn lead panels; a big-number stat strip (60 mph gusts, the 15% Taiwan rate, an 8.5 ft record tide, the 2030 climate target, a five-year Wallabies exile ending, a 200 ha kelp farm); a numbered grid of eight more stories, each with its own drawn icon; a dotted world map whose numbered pins match the story numbers; an ALSO ON THURSDAY list of five further stories; and a DATE CHECK box that names the stories deliberately left out as 25 November's news. Every story was date-checked against 26 November 2026 reporting — the day is thin this early in UTC (wires read up to 00:45 UTC), so the page carries 16 solidly verified stories rather than padding with 25 November news.

## Run it

```sh
node main.ts
```

The program copies the repository's `entry.png` to `/output/entry.png` (or to `$MAKEFUN_OUTPUT_DIR/entry.png` outside the grader), after checking it against the gate's limits (PNG or JPEG, at most 1 MiB, at most 1024 by 1024). Node 22, standard library only.

The image itself is composed by `compose.py` (Python + PIL): the day's stories, researched from 26 November's reporting, drawn and set as a legible illustrated front page at 1024 by 1024. Rebuild it with `python3 compose.py`.
