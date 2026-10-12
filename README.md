# course-material-to-video

Match course notes to the YouTube videos (and the exact minutes) that teach them,
so you can self-learn a course without hunting through YouTube.

**Status: layers 1–3 built; layer 3 tested on one section.**

| Layer | What it does | Status |
|---|---|---|
| 1. Fetch | YouTube search, video facts (views, likes, length), timestamped transcripts, local cache | ✅ |
| 2. Interface | MCP server so any Claude app can call layer 1 | ✅ |
| 3. Judgment | Rules (a Claude skill, `skill/SKILL.md`) for picking the fewest videos that, with the notes, explain every concept in a section | ✅ draft |
| 4. Output | A per-section video map: the picture → the full idea → read the notes → check your understanding | ✅ draft |

## Repo layout

```
cmv/                 the Python package (cmv = course material → video)
  youtube.py         layer 1: YouTube search, video facts, transcripts, cache, quota
  server.py          layer 2: MCP server exposing layer 1 as tools
  safety.py          cleans/fences text written by strangers before Claude sees it
tests/               offline tests: no network, no key
skill/SKILL.md       layer 3: the rules Claude follows to build a video map
scripts/live_check.py  starts the server like a Claude app does and calls every tool
cache/               saved API results and transcripts (not committed)
.env                 your YouTube API key (not committed)
```

## Setup

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env    # then paste your YouTube Data API v3 key into .env
.venv/bin/python -m unittest          # offline tests
.venv/bin/python scripts/live_check.py  # live check (needs the key)
```

Transcripts need no key. Search and video facts do (free key, 10,000 units a day;
one search costs 101, so about 95 searches a day). Everything is cached in `cache/`.

## MCP tools (layer 2)

| Tool | What it returns | Quota |
|---|---|---|
| `search_videos(query, max_results, channel)` | Videos with length, views, likes per 1k views, link | 101, or 0 if searched before |
| `video_details(video_ids)` | Same facts plus the uploader's description (often has chapters) | 1 per 50 |
| `get_transcript(video_id, start_seconds, end_seconds)` | Timestamped lines, optionally just a time window | 0 |
| `find_in_transcript(video_id, terms)` | Only the passages that mention the terms, with links that open at that moment | 0 |
| `quota_status()` | Units used today | 0 |

Start it with `.venv/bin/python -m cmv.server` (Claude apps do this for you once it's registered).
Uploader-written text comes back inside `UNTRUSTED` fences so Claude treats it as data, not instructions.
