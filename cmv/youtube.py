"""
youtube.py — layer 1: fetch facts about YouTube videos. No judging, no AI.

Three things, all cached on disk so asking twice costs nothing:

    search_videos(query)    -> videos matching a query, with views/likes/length
    video_details(ids)      -> the same facts for videos you already know
    get_transcript(id)      -> what is said, as [{start, text}] with timestamps

Plus channel_id(handle) to turn "@3blue1brown" into an id for search filtering.

Cost (YouTube Data API, 10,000 units a day on a free key):
    search_videos  = 101 units  (search is 100, details for the results is 1)
    video_details  = 1 unit per 50 videos
    channel_id     = 1 unit
    get_transcript = 0 units    (no key; uses youtube-transcript-api)

Security:
  - the key comes from the YOUTUBE_API_KEY environment variable or .env,
    and is scrubbed out of every error message (Google's errors can echo it)
  - titles and channel names are cleaned with safe_field() on the way in;
    descriptions and transcripts are stored raw and MUST be fenced with
    safety.fence() before they are shown to Claude (layer 2 does this)
"""

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .safety import safe_field

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache"
API_ROOT = "https://www.googleapis.com/youtube/v3/"

DETAILS_MAX_AGE_DAYS = 30   # view counts drift slowly; transcripts never expire
MIN_SECONDS = 120           # anything shorter is a Short, not a lesson
TRANSCRIPT_GAP_SECONDS = 1  # be gentle; YouTube blocks IPs that fetch too fast

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")

_key = None


class YouTubeError(RuntimeError):
    """Something went wrong talking to YouTube. Message never contains the key."""


# --- key ------------------------------------------------------------------

def _api_key():
    global _key
    if _key:
        return _key
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    env = ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("YOUTUBE_API_KEY="):
                key = line.split("=", 1)[1].strip().strip("\"'")
    if not key or key == "paste-your-key-here":
        raise YouTubeError("No YouTube API key. Put YOUTUBE_API_KEY=... in .env (see .env.example).")
    _key = key
    return _key


def _scrub(text):
    return str(text).replace(_key, "***KEY-HIDDEN***") if _key else str(text)


# --- cache ----------------------------------------------------------------

def _cache_path(kind, name):
    path = CACHE / kind / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _cache_read(kind, name, max_age_days=None):
    path = _cache_path(kind, name)
    if not path.exists():
        return None
    if max_age_days is not None and time.time() - path.stat().st_mtime > max_age_days * 86400:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _cache_write(kind, name, data):
    _cache_path(kind, name).write_text(json.dumps(data, indent=1), encoding="utf-8")


def _record_quota(units):
    # Google resets the quota at midnight Pacific time.
    today = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    log = _cache_read("quota", "usage") or {}
    log[today] = log.get(today, 0) + units
    _cache_write("quota", "usage", log)


def quota_used_today():
    today = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    return (_cache_read("quota", "usage") or {}).get(today, 0)


# --- the one function that talks to the YouTube Data API ------------------

def _api_get(endpoint, params, cost):
    params = dict(params, key=_api_key())
    url = API_ROOT + endpoint + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            data = json.load(response)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            reason = json.loads(body)["error"]["message"]
        except Exception:
            reason = body[:300]
        raise YouTubeError(f"YouTube API error {e.code}: {_scrub(reason)}") from None
    except Exception as e:
        raise YouTubeError(f"Could not reach YouTube: {_scrub(e)}") from None
    _record_quota(cost)
    return data


# --- public calls ---------------------------------------------------------

def _seconds(iso):
    """'PT1H2M30S' -> 3750."""
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    d, h, mi, s = (int(g or 0) for g in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def _video_from_api(item):
    stats = item.get("statistics", {})
    snippet = item["snippet"]
    views = int(stats.get("viewCount", 0))
    likes = int(stats["likeCount"]) if "likeCount" in stats else None  # can be hidden
    return {
        "id": item["id"],
        "url": f"https://www.youtube.com/watch?v={item['id']}",
        "title": safe_field(snippet.get("title", ""), 200),
        "channel": safe_field(snippet.get("channelTitle", ""), 80),
        "channel_id": snippet.get("channelId", ""),
        "published": snippet.get("publishedAt", "")[:10],
        "seconds": _seconds(item["contentDetails"].get("duration")),
        "views": views,
        "likes": likes,
        "likes_per_1k_views": round(likes / views * 1000, 1) if likes is not None and views else None,
        "creator_captions": item["contentDetails"].get("caption") == "true",  # auto-captions not counted; get_transcript usually still works
        "description": snippet.get("description", ""),  # RAW: fence before showing
    }


def video_details(ids):
    """Facts for known video ids. Cached for DETAILS_MAX_AGE_DAYS."""
    ids = [i for i in dict.fromkeys(ids) if VIDEO_ID_RE.match(i)]
    found = {i: v for i in ids if (v := _cache_read("videos", i, DETAILS_MAX_AGE_DAYS))}
    missing = [i for i in ids if i not in found]
    for start in range(0, len(missing), 50):
        data = _api_get("videos", {"part": "snippet,contentDetails,statistics",
                                   "id": ",".join(missing[start:start + 50])}, cost=1)
        for item in data.get("items", []):
            video = _video_from_api(item)
            _cache_write("videos", video["id"], video)
            found[video["id"]] = video
    return [found[i] for i in ids if i in found]


def search_videos(query, max_results=10, channel_id=None):
    """
    Videos matching `query`, any upload date, Shorts removed. Most relevant first.
    Pass channel_id to search only one channel (e.g. a trusted teacher).

    A search costs 100 units whether it returns 5 results or 50, so this always
    asks for 50 and caches them; max_results only trims what is returned.
    """
    params = {"part": "snippet", "q": query, "type": "video", "order": "relevance",
              "maxResults": 50, "relevanceLanguage": "en"}
    if channel_id:
        params["channelId"] = channel_id
    name = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:16]
    ids = _cache_read("searches", name)
    if ids is None:
        data = _api_get("search", params, cost=100)
        ids = [item["id"]["videoId"] for item in data.get("items", [])]
        _cache_write("searches", name, ids)
    return [v for v in video_details(ids) if v["seconds"] >= MIN_SECONDS][:max_results]


def channel_id(handle):
    """'@3blue1brown' -> 'UCYO_jab_esuFRV4b17AJtAw'. Cached forever."""
    handle = handle if handle.startswith("@") else "@" + handle
    cached = _cache_read("channels", handle.lower())
    if cached:
        return cached["id"]
    items = _api_get("channels", {"part": "id", "forHandle": handle}, cost=1).get("items", [])
    if not items:
        raise YouTubeError(f"No channel found for {safe_field(handle, 60)}")
    _cache_write("channels", handle.lower(), {"id": items[0]["id"]})
    return items[0]["id"]


def get_transcript(video_id):
    """
    [{"start": seconds, "text": "..."}, ...] in English. Cached forever. No API key.
    Raises YouTubeError if the video has no captions or YouTube blocks the request.
    The text is RAW: fence it before showing it to Claude.
    """
    if not VIDEO_ID_RE.match(video_id or ""):
        raise YouTubeError("Not a YouTube video id.")
    cached = _cache_read("transcripts", video_id)
    if cached is not None:
        return cached
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        raise YouTubeError("Run: pip install -r requirements.txt") from None
    time.sleep(TRANSCRIPT_GAP_SECONDS)
    try:
        fetched = YouTubeTranscriptApi().fetch(video_id, languages=("en", "en-US", "en-GB"))
    except Exception as e:
        raise YouTubeError(f"No transcript for {video_id}: {type(e).__name__}") from None
    lines = [{"start": round(s.start, 1), "text": s.text} for s in fetched if s.text.strip()]
    _cache_write("transcripts", video_id, lines)
    return lines
