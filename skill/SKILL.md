---
name: course-material-to-video
description: Build a video map for a section of course notes - for each concept in the section, the YouTube clip (video + exact timestamps) that explains it, plus a flag for any part of the notes no video covers. For self-learning a course from its notes. Use when asked which video to watch for a lesson/section/chapter, to "map" course notes to YouTube, or to self-learn a section from videos. Requires the course-material-to-video MCP tools (search_videos, find_in_transcript, get_transcript, video_details, quota_status).
---

# Course material → video map

The student is self-learning a course from its notes, using YouTube instead of
lectures. For each section they want a simple map: **each concept → the clip
that explains it**, and a flag for anything in the notes no video covers. The
goal is a solid understanding of every concept, with no gaps.

Every "this clip explains X" and every timestamp must come from a transcript
tool result, never from a title or memory.

## 1. List the concepts

Read the section in the course notes (in this project's files). List every
definition, theorem and technique, in the notes' order. Split theorems into
their parts, e.g. Theorem 2.3.3 (a), (b), (c).

Next to each, write the **standard names** YouTube uses. Courses invent labels:
"System–Rank Theorem" is "rank and solvability", "full row rank / full column
rank", "Rouché–Capelli" elsewhere. Search and check with the standard names.

## 2. Search

Each new search costs 101 of 10,000 daily units; repeats are free. Call
`quota_status` first. Use **up to 5 new searches per section**.

Search trusted channels first, with `search_videos(query, channel=...)`. If the
project has a note listing trusted channels for this course, use it. Otherwise,
for linear algebra: `@3blue1brown` (intuition), `@mitocw` (Strang's 18.06,
complete theory), `@DrTrefor` (clear, course-level), `@khanacademy` (worked
examples). Then use general searches for whatever is still uncovered.

Keep every query to **3–6 words** using a standard name ("rank augmented matrix
consistency"). Long queries return generic matches. For a lecture you already
know is relevant, `video_details` (1 unit) plus its transcript is cheaper than
a search.

Skip videos under ~10,000 views, under ~5 likes per 1k views, or with no
English transcript, unless nothing else covers a concept (then say so).

## 3. Check

For each promising candidate, use `find_in_transcript` with the standard names,
and `get_transcript` with a time window to read the passage. Record which
concepts it **explains** (says what and why, not just mentions or applies), and
where.

- Check each part of a theorem separately. A video can teach part (a) and skip
  part (b). (Tested: a "consistency by rank method" video covered the unique and
  no-solution cases and never mentioned infinitely many solutions.)
- Before giving up on a concept, try one more short query with another name.

## 4. Pick

Choose the **smallest set of clips that covers every concept**, in this order:

1. Only clips that passed the check.
2. Fewest clips: one clip covering four concepts beats four clips.
3. Explanation beats recipe: a clip that shows *why* beats one that only
   lists steps. A recipe is fine as a worked example.
4. A clip beats a whole video: only the minutes that match the section. Use
   judgment about where to start. Start at the **beginning of the video's
   segment on that idea**, such as the start of the topic or the worked problem
   that builds up to the theorem, not at the moment the theorem is stated.
   (Tested: Strang shows Theorem 2.4.4 *through* a problem; starting at the
   statement skipped the build-up. A topic's opening definition was skipped
   too when a clip started 51 s in.) If the segment relies on an example set up
   earlier in the video, say where in the bridge ("the matrix is at 0:52").
5. **Show why, in any notation.** Prefer clips that *show why* (a picture,
   a worked reason) over clips that only state the theorem. Never filter by
   notation: a great explanation in different symbols beats a weak one in the
   notes' symbols. Different notation is handled by the bridge (see Output).
   (Tested: a student understood a visual explanation start to finish, but
   couldn't follow a lecture that stated the same theorem.)
6. Whatever no picked clip explains goes in the notes flag.

## 5. Output

Exactly this, in plain words, in the notes' order:

```
§<number> <title>   (≈<total minutes> min of video)

| Concepts | Video | Watch | Bridge |
|---|---|---|---|
| <plain-language concepts this clip explains> | <channel>, <short title> | [<start>–<end>](<link opening at start>) | <see below> |

📖 Videos don't cover these, so read them in the notes:
- <Example/Definition/Theorem number>: <what it is, in plain words>
```

**The bridge** is Claude's own short explanation that connects the clip to the
notes, in plain words. Write one only when it's needed:

- **Translate:** the video's terms or notation → the notes' (e.g. "Strang's
  'null space' = all solutions of the associated homogeneous system, Def 2.4.3";
  "Ax = b is just the system [A | b] written as one equation").
- **Fill a small gap:** a step or reason the clip skips, in 1–2 sentences.
- **Connect:** how the clip's idea becomes the notes' theorem (e.g. "this
  picture is Theorem 2.4.4").

Every bridge cites the notes' definition/theorem/example number it relies on, so
the student can check it. Bridges are not checked against a video, so keep them
short and stick to what the notes say. Anything bigger than a bridge belongs in
📖.
