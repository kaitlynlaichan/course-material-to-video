# course-material-to-video

Match course notes to the YouTube videos (and the exact minutes) that teach them,
so you can self-learn a course without hunting through YouTube.

You ask Claude for a section of your notes. It lists every concept, searches
YouTube, reads the transcripts to confirm which clips really explain each one, and
gives you the fewest clips that cover the section, plus a list of anything you
still need to read in the notes.

**Status: working.** I've used it on 7 sections of a first-year linear algebra course.

## Example output

A real video map for a section on matrix algebra, shortened for this README.
Numbers such as "Def 3.1.14" point to the course notes.

> 💡 **Big idea:** this section is mostly definitions. Matrices are added and scaled
> entry by entry, so they follow the same rules as vectors. The one new operation is
> the transpose: rows become columns.
>
> **§3.1 Matrix Algebra** (about 12 min of video)
>
> | Concepts | Video | Watch | Bridge |
> |---|---|---|---|
> | Matrix entries and size; addition and scaling; the transpose | Dr. Trefor Bazett, Algebraic operations on Matrices | [whole video, 8 min](https://www.youtube.com/watch?v=HlaZrTcgmWw) | Addition only works for matrices of the same size (Def 3.1.9). Transpose: entry a_ij moves to position (j, i), so an m×n matrix becomes n×m (Def 3.1.14). |
> | Symmetric and skew-symmetric matrices | BYJU'S, Symmetric and Skew symmetric matrix | [whole video, 4 min](https://www.youtube.com/watch?v=v5abfTlztTc) | Symmetric means Aᵀ = A; skew-symmetric means Aᵀ = −A. |
>
> 📖 **Videos don't cover these, so read them in the notes:**
> - Definition 3.1.4: the zero matrix
> - Theorem 3.1.16: properties of the transpose

The **Bridge** column is Claude's own short explanation connecting the clip to the
notes. It is not from the video, so it cites the notes for you to check.

## How it works

| Layer | What it does |
|---|---|
| 1. Fetch | YouTube search, video facts (views, likes, length), timestamped transcripts, local cache |
| 2. Interface | MCP server so any Claude app can call layer 1 |
| 3. Judgment | Rules (a Claude skill, `skill/SKILL.md`) for picking the fewest videos that, with the notes, explain every concept in a section |
| 4. Output | A per-section video map: the big idea, a concept → clip table with bridges, and what to read in the notes |

Three decisions worth knowing about:

- **Clips are checked, not guessed.** The skill tells Claude that every "this clip
  explains X" and every timestamp must come from a transcript, never a title or memory.
- **Video text is treated as untrusted.** Anyone can upload a video, so a description
  or transcript could try to give Claude instructions. Titles and channel names are
  cleaned, and longer text is wrapped in `UNTRUSTED` fences with an unguessable marker
  (`cmv/safety.py`).
- **The free API quota goes a long way.** Search is the expensive call, so results are
  cached on disk and repeating a search costs nothing.

The "Tested:" notes in `skill/SKILL.md` record rules that changed after I used a map
to study and found something that didn't work.

## Repo layout

```
cmv/                 the Python package (cmv = course material → video)
  youtube.py         layer 1: YouTube search, video facts, transcripts, cache, quota
  server.py          layer 2: MCP server exposing layer 1 as tools
  safety.py          cleans/fences text written by strangers before Claude sees it
tests/               offline tests: no network, no key
skill/SKILL.md       layer 3: the rules Claude follows to build a video map
scripts/live_check.py  starts the server like a Claude app does and calls the tools
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

To use it in Claude Desktop, add this to `claude_desktop_config.json`, with your own
path to this folder, and add `skill/SKILL.md` to your Claude app as a skill:

```json
{
  "mcpServers": {
    "course-material-to-video": {
      "command": "/path/to/course-material-to-video/.venv/bin/python",
      "args": ["-m", "cmv.server"],
      "env": { "PYTHONPATH": "/path/to/course-material-to-video" }
    }
  }
}
```

## MCP tools (layer 2)

| Tool | What it returns | Quota |
|---|---|---|
| `search_videos(query, max_results, channel)` | Videos with length, views, likes per 1k views, link | 101, or 0 if searched before |
| `video_details(video_ids)` | Same facts plus the uploader's description (often has chapters) | 1 per 50 |
| `get_transcript(video_id, start_seconds, end_seconds)` | Timestamped lines, optionally just a time window | 0 |
| `find_in_transcript(video_id, terms)` | Only the passages that mention the terms, with links that open at that moment | 0 |
| `quota_status()` | Units used today | 0 |

## How this was built

Built with [Claude Code](https://claude.com/claude-code). I set the goal and the rules
for what makes a good map, then tested the maps on my own coursework and changed the
rules based on what did and didn't help me learn.

## License

[MIT](LICENSE)
