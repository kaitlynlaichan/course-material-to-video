---
name: course-material-to-video
description: Build a video map for a section of course notes - the fewest YouTube videos (or exact segments) that, together with the notes, leave no gaps for that section's problems. The student watches, reads, then does the problem set. Use when asked which video to watch for a lesson/section/chapter, to "map" course notes to YouTube, or to self-learn a section from videos. Requires the course-material-to-video MCP tools (search_videos, find_in_transcript, get_transcript, video_details, quota_status).
---

# Course material → video map

The student is self-learning instead of going to lectures. The goal is to be
**fully ready for the section's problems** with the least time spent. So the
map must:

- leave **no gaps**: every idea the problems need is learned somewhere, from a
  video or from a named place in the notes
- be **short**: at most two things to watch, plus one optional worked example
- **only promise what was checked**: every "this video covers X" and every
  timestamp comes from a transcript tool result, never from a title or memory

## 1. Work backwards from the problems

Read the section in the course notes (in this project's files), plus its
practice problems and any assigned problem set for it in the project files.

Write the **checklist**: each definition, theorem and problem type the problems
need, in the notes' order. For each item note:

- which problems use it (e.g. "2.3.3, 2.3.4"), and mark the most-used ones ★
- the **standard names** YouTube uses next to the course's own name. Courses
  invent labels: "System–Rank Theorem" is "consistency by rank method",
  "rank of augmented matrix", "Rouché–Capelli" elsewhere. Search and verify
  with the standard names.

## 2. Find candidates (quota-aware)

Each new search costs 101 of 10,000 daily units; repeats are free. Call
`quota_status` first. Budget **up to 5 new searches per section**.

1. Trusted channels first, with `search_videos(query, channel=...)`:
   `@3blue1brown` (big-picture intuition), `@DrTrefor` (clear, course-level),
   `@mitocw` (Strang lectures, deep dives), `@khanacademy` (worked examples).
2. Then general searches for whatever is still uncovered.

Keep every query to **3–6 words** using a standard name ("rank augmented matrix
consistency", "values of k no solution"). Long queries make YouTube fall back
to generic matches. (Tested: a 17-word query found nothing that said "rank";
a 4-word query found the right video.)

Popularity is a filter, not a score. Skip videos under ~10,000 views or under
~5 likes per 1k views unless nothing else covers an item (then say so). Skip
videos with no English transcript, since they can't be verified.

## 3. Verify coverage

For each promising candidate, call `find_in_transcript` with the standard names
of the checklist items. Record which items it actually **explains** (not just
mentions) and the exact start and end times. Use `get_transcript` with a time
window when you need context to judge that, or to find where a segment starts.

Check each part of a theorem separately. A video can teach part (a) and skip
part (b). (Tested: a "consistency by rank method" video covered the unique and
no-solution cases and never mentioned infinitely many solutions.)

Before declaring a ★ item a gap, try one more short query with a different
standard name. That is how gaps usually get filled.

## 4. Choose

- **Watch 1:** the clip that builds the big-picture intuition for the section.
  Prefer a segment over a whole video when the rest isn't in this section. Say
  what the segment assumes, and when to start from 0:00 instead.
- **Watch 2:** only if a ★ item is still uncovered. Never more than two watches.
- **Problem help:** one worked example matched to the hardest ★ problem type.
  Name the exact problems it helps with. It is optional: watch only if stuck.
- **Learn from the notes:** every checklist item no chosen video explains, with
  the exact theorem / example numbers to read. This is normal, not a failure.
  The point is that nothing is unaccounted for.
- If a video defines something differently from the notes (e.g. rank as
  "dimension of the column space" vs "number of leading entries in REF"), say in
  one line that both are the same idea seen two ways.
- If the section relies on an earlier section, name it in one line.

## 5. Output

Use exactly this shape, in plain words. Then one line asking whether the picks
helped.

```
§<number> <title>   (≈<total minutes> min of video, <problem help> optional)

1. ▶ Watch: <channel>, "<title>", <start>–<end> (<minutes> min)
   <link that opens at start>
   You'll learn: <plain-language list>
   (Assumes <x>. If that's new, start at 0:00.)        ← only if true
2. ▶ Watch: ...                                         ← only if needed
3. 📖 Read: notes §<number>. Focus on <theorem/example numbers>, which cover
   <items no video explained>.
4. ✏️ Then do the problems. If stuck on <problem numbers> (<problem type>):
   <channel>, "<title>", <start>–<end>, <link>

Before you start: §<earlier section> (<idea>) is assumed.  ← only if relevant
```

Then a **Ready for the problems?** table, so the student can see there are
no gaps:

| You need | For problems | Learned from |
|---|---|---|
| <checklist item> | <numbers> | Watch 1 <mm:ss> / Notes <Example x> |
