---
name: course-material-to-video
description: Build a video map for a section of course notes - the fewest YouTube videos (or exact segments) that, together with the notes, give a deep understanding of every concept in the section, so the student can apply it to any problem. Use when asked which video to watch for a lesson/section/chapter, to "map" course notes to YouTube, or to self-learn a section from videos. Requires the course-material-to-video MCP tools (search_videos, find_in_transcript, get_transcript, video_details, quota_status).
---

# Course material → video map

The student is self-learning instead of going to lectures. The goal is a
**solid understanding of every concept in the section**: what it is, why it's
true, and how to use it, so they can handle any problem, not just familiar
ones. Problem sets are the check, not the target.

The map must:

- leave **no gaps**: every concept in the section is learned somewhere, from a
  video or from a named place in the notes
- prefer **explanation over recipe**: a video that shows *why* beats one that
  only shows the steps
- stay **short**: at most two things to watch, plus one optional worked example
- **only promise what was checked**: every "this video covers X" and every
  timestamp comes from a transcript tool result, never from a title or memory

## 1. List the concepts

Read the section in the course notes (in this project's files). List every
definition, theorem and technique, in the notes' order. Break theorems into
their parts, e.g. Theorem 2.3.3 (a), (b), (c).

For each concept, write the **standard names** YouTube uses next to the
course's own name. Courses invent labels: "System–Rank Theorem" is "rank and
solvability", "full row rank / full column rank", "Rouché–Capelli" elsewhere.
Search and verify with the standard names.

## 2. Find candidates (quota-aware)

Each new search costs 101 of 10,000 daily units; repeats are free. Call
`quota_status` first. Budget **up to 5 new searches per section**.

Search trusted channels first, with `search_videos(query, channel=...)`. If the
project has a note listing trusted channels for this course, use it. Otherwise,
for linear algebra:

- `@3blue1brown`: the picture, why things are true
- `@mitocw`: Strang's 18.06 lectures, complete theory with reasons
- `@DrTrefor`: clear and course-level, often bridges picture and computation
- `@khanacademy`: step-by-step worked examples

Then use general searches for whatever is still uncovered. Keep every query to
**3–6 words** using a standard name ("rank augmented matrix consistency").
Long queries make YouTube fall back to generic matches.

For a long lecture you already know is relevant, `video_details` (1 unit) plus
the transcript is cheaper than searching.

Popularity is a filter, not a score. Skip videos under ~10,000 views or under
~5 likes per 1k views unless nothing else covers a concept (then say so). Skip
videos with no English transcript, since they can't be verified.

## 3. Verify coverage

For each promising candidate, call `find_in_transcript` with the standard names.
Record which concepts it **explains** (not just mentions or applies), and the
exact start and end. Use `get_transcript` with a time window to judge that and
to find clean start and end points.

Check each part of a theorem separately. A video can teach part (a) and skip
part (b). (Tested: a "consistency by rank method" video covered the unique and
no-solution cases and never mentioned infinitely many solutions.)

Judge depth: does it say *why*? A recipe ("compute both ranks, compare") is
fine for a worked example but not as the main explanation.

Before declaring a concept a gap, try one more short query with a different
standard name.

## 4. Choose

- **Watch 1 (the picture):** the clip that gives the intuition, usually the
  geometric meaning. Prefer a segment when the rest of the video isn't in this
  section. Say what it assumes, and when to start from 0:00 instead.
- **Watch 2 (the full idea):** the clip that explains the section's main
  theorem(s) completely and with reasons. A 20-minute segment of a strong
  lecture beats three short partial videos.
- **Read:** the notes for the precise statements, plus any concept no chosen
  video explains, with exact theorem / example numbers. This is normal, not a
  failure. The point is that nothing is unaccounted for.
- **Check your understanding:** 2–3 items *from the notes* (an exercise, or an
  example to redo without looking) that test whether the ideas transfer. Never
  invent problems.
- **Worked example (optional):** one video that applies the ideas step by step,
  for the hardest technique in the section.
- If a video defines something differently from the notes (e.g. rank as
  "dimension of the column space" vs "number of leading entries in REF"), say in
  one line that both are the same idea seen two ways, and how they connect.
- If the section relies on an earlier section, name it in one line.

## 5. Output

Use exactly this shape, in plain words. Then one line asking what felt unclear.

```
§<number> <title>   (≈<total minutes> min of video)

1. ▶ The picture: <channel>, "<title>", <start>–<end> (<minutes> min)
   <link that opens at start>
   You'll understand: <plain-language list>
   (Assumes <x>. If that's new, start at 0:00.)        ← only if true
2. ▶ The full idea: <channel>, "<title>", <start>–<end> (<minutes> min)
   <link>
   You'll understand: ...
3. 📖 Read: notes §<number>, for the precise statements. Also covers <concepts
   no video explained> (<theorem/example numbers>).
4. ✅ Check your understanding: <2–3 items from the notes>
   Worked example if a technique feels shaky: <channel>, "<title>", <link>

Before you start: §<earlier section> (<idea>) is assumed.  ← only if relevant
```

Then a **coverage table**, so the student can see there are no gaps:

| Concept | Learned from |
|---|---|
| <concept, in the notes' order> | Watch 1 <mm:ss> / Watch 2 <mm:ss> / Notes <number> |
