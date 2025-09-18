"""Lightweight Nigerian English/Pidgin text normalization."""
import re
from typing import Tuple

MAX_CHARS = 500  # safety

_SPACES = re.compile(r"\s+")
_DUP_PUNCT = re.compile(r"([!?.,])\1{1,}")
_PIDGIN_COMPOUND = [
    ("well-well", "well, well"),
    ("small small", "small-small"),
]


def normalize(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be string")
    t = text.strip()
    t = _SPACES.sub(" ", t)
    # soften repeated punctuation
    t = _DUP_PUNCT.sub(r"\1", t)
    # pidgin tweaks
    for a, b in _PIDGIN_COMPOUND:
        t = re.sub(re.escape(a), b, t, flags=re.IGNORECASE)
    # ensure sentence end
    if not t.endswith((".", "!", "?")):
        t += "."
    if len(t) > MAX_CHARS:
        t = t[:MAX_CHARS]
    return t
