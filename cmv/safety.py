"""
safety.py — make text written by strangers (video titles, descriptions,
transcripts) safe to hand to Claude.

Reused from an earlier project of mine, where adversarial testing found the
problems described in the notes on each function.
"""



# ---------------------------------------------------------------------------
# UNTRUSTED TEXT — one implementation, used everywhere.
#
# Everything fetched from YouTube was written by a stranger, and all of it ends
# up in front of Claude. It is DATA, never instructions.
#
# There are TWO separate jobs here and they are not interchangeable:
#
#   fence()      wraps stranger text so it cannot impersonate anything around
#                it. For the BODY of a thing.
#   safe_field() makes a stranger's value safe to interpolate into a line we
#                wrote. For values that go ABOVE the fence, in our own voice.
#
# Fencing the body is not enough on its own. If a channel name lands unescaped
# in the header, the attacker never has to break out of a fence — they were
# handed the trusted voice directly. safe_field() exists because an adversarial
# pass pointed out the header separator is "|", not a newline, so collapsing
# whitespace stopped nothing.
# ---------------------------------------------------------------------------

import re as _re
import secrets as _secrets
import unicodedata as _ud

# Zero-width, direction-control and variation-selector characters. These defeat
# any check that looks for a WORD: "UNTR<zero-width space>USTED" is not
# "UNTRUSTED" to a regex, and is identical to it on screen. Removed before
# anything is tested, and removed from stored text so nothing invisible reaches
# Claude.
# ︀-️ are variation selectors: '⚠️' (a warning sign) is TWO
# codepoints, so stripping the sign alone left an invisible selector behind.
_INVISIBLE = _re.compile(r"[­​-‏‪-‮⁠-⁤︀-️﻿]")

# Characters that look exactly like the field separator. NFKC folds the
# full-width one; these are the ones it does not fold.
_PIPES = "|\u01c0\u01c1\u2223\u2502\u2758\u23d0\u007c"

# Unicode categories with no place in a stranger's plain-text value:
# Cc control · Cf format/zero-width · Co private use · Cs surrogate
# So symbols (emoji, ★, ✔, box-drawing) · Sk modifier · Sm math (∣)
_BANNED_CATEGORIES = {"Cc", "Cf", "Co", "Cs", "So", "Sk", "Sm"}


def scrub_markers(text):
    """
    Remove fence-marker-shaped lines. LINEAR, and deliberately not a regex.

    ⚠️ This used to be a regex: `-{2,}[^\n]*untrusted[^\n]*`. It backtracks
    catastrophically. Measured: 800 dashes 0.8s, 1,500 dashes 5.4s, 3,000 dashes
    44s. One YouTube description consisting of a long run of dashes could have
    hung the program with no output, and no test would have caught it because
    none fed it a dash run. Found by an adversarial pass on the built code, not
    by review of the plan.

    A plain substring test over each line is linear and does the same job.
    """
    out = []
    for line in (text or "").splitlines():
        bare = _INVISIBLE.sub("", line)
        probe = bare.lower()
        out.append("[marker removed]" if ("untrusted" in probe and "--" in bare) else bare)
    return "\n".join(out)


def fence(label, body):
    """
    Wrap stranger-written text so it cannot impersonate anything around it.

    TWO INDEPENDENT DEFENCES, and that is deliberate:
      1. the nonce — the closing marker is unguessable, so the text cannot end
         its own fence and start writing in the trusted voice;
      2. scrub_markers — marker-shaped text is removed anyway, and invisible
         characters are stripped so a marker cannot hide inside a word.

    ⚠️ Either one alone defeats the simple escape attack, which is exactly why
    each needs its OWN test. In testing, the scrubber was once silently removed
    and every check still passed because the nonce covered for it. A defence
    that can rot while every check passes is not a defence.
    """
    nonce = _secrets.token_hex(8)
    return (f"--- BEGIN UNTRUSTED {label} {nonce} ---\n"
            f"{scrub_markers(body)}\n"
            f"--- END UNTRUSTED {label} {nonce} ---")


def safe_field(value, limit=120):
    """
    Make a stranger's value safe to drop into a line WE wrote.

    ⚠️ ALLOWLIST, NOT DENYLIST. The first version listed the exact characters to
    strip: `|` and five emoji. An adversarial pass walked straight through it
    with `｜` and `│` (identical-looking separators), `★` and
    `✔` (star and tick), and a right-to-left override that visually
    reorders the line. A denylist only stops the characters somebody thought of.

    So: normalise, drop every category that has no business in a plain value,
    drop the separator and its lookalikes, collapse whitespace, remove marker
    text, truncate. Letters and digits in any script survive.
    """
    s = _ud.normalize("NFKC", str(value if value is not None else ""))
    s = _INVISIBLE.sub("", s)
    kept = [ch for ch in s
            if ch not in _PIPES and _ud.category(ch) not in _BANNED_CATEGORIES]
    cleaned = " ".join("".join(kept).split())
    cleaned = scrub_markers(cleaned)
    return " ".join(cleaned.split())[:limit]



