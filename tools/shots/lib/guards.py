"""Decide whether a take shows the page, or an error or block page instead.

A take that fails a guard is kept in out/ for inspection but can never be
promoted into images/. A figure whose subject *is* a refusal says so with
`expect: {block: true}`, and then the guard requires one.
"""
import re

from PIL import Image, ImageStat

# Checked against the page title and the first few thousand characters of its
# text. Each pattern names what it usually means, and whether it tends to pass
# on its own (a gateway hiccup: worth a polite retry) or not (a block: stop).
BLOCK_PATTERNS = [
    (r"Just a moment\.\.\.|Checking your browser|cf-browser-verification", "a Cloudflare challenge", False),
    (r"Attention Required", "a Cloudflare block", False),
    (r"Access denied", "an access-denied page", False),
    (r"You've been blocked|You have been blocked|Request blocked", "a block page", False),
    (r"Too Many Requests|rate limit(ed)? exceeded", "a rate limit", True),
    (r"Bad Gateway|Gateway Time-?out|Service Unavailable", "a gateway error", True),
    (r"upstream request failed|Fail with status|Temporarily Offline", "a Wayback Machine error", True),
    (r"verify you are (a )?human|captcha", "a human check", False),
]
HEAD_CHARS = 3000


def page_problems(status, title, text, expect):
    """Problems with a loaded page, and whether they look temporary."""
    problems = []
    want = expect.get("status", 200)
    if status != want:
        problems.append(f"HTTP status {status}, expected {want}")
    head = f"{title}\n{text[:HEAD_CHARS]}"
    hits = [(label, temporary) for pattern, label, temporary in BLOCK_PATTERNS
            if re.search(pattern, head, re.I)]
    if expect.get("block"):
        if not hits:
            problems.append("expected a block or error page, but the page looks normal")
        return problems, False
    if hits:
        problems.append("the page looks like " + " and ".join(sorted({label for label, _ in hits})))
    return problems, bool(hits) and all(temporary for _, temporary in hits)


def image_problems(path):
    """Problems visible in the image itself."""
    with Image.open(path) as img:
        gray = img.convert("L")
        spread = ImageStat.Stat(gray).stddev[0]
    if spread < 3:
        return [f"the image is nearly blank (pixel spread {spread:.1f})"]
    return []


def retryable(status=None, error=None):
    """A 5xx or a dropped connection is worth another polite try; a refusal is not."""
    if status is not None and status >= 500:
        return True
    if error and any(s in error for s in ("ERR_CONNECTION_RESET", "ERR_CONNECTION_CLOSED",
                                          "ERR_EMPTY_RESPONSE", "ERR_TIMED_OUT", "Timeout")):
        return True
    return False


def policy_block(error):
    """The proxy refused the host. Report it; never retry or route around it."""
    return bool(error) and "ERR_TUNNEL_CONNECTION_FAILED" in error
