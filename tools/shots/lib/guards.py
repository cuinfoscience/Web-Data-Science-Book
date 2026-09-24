"""Decide whether a take shows the page, or an error or block page instead.

A take that fails a guard is kept in out/ for inspection but can never be
promoted into images/. A figure whose subject *is* a refusal says so with
`expect: {block: true}`, and then the guard requires one. A figure whose
subject is a host that no longer answers says so with `expect: {error: ...}`,
the error Chrome reports; the take is then Chrome's own error page.
"""
import json
import os
import re
import urllib.parse
import urllib.request

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
# Public DNS over HTTPS, asked through the session's proxy like every other request.
DOH = os.environ.get("SHOTS_DOH", "https://dns.google/resolve")
RCODES = {0: "NOERROR", 2: "SERVFAIL", 3: "NXDOMAIN", 5: "REFUSED"}


def page_problems(status, title, text, expect):
    """Problems with a loaded page, and whether they look temporary."""
    if expect.get("error"):
        # The subject is a page that never loaded, so there is no status to check.
        if status is not None:
            return [f"expected the page not to load ({expect['error']}), "
                    f"but it loaded with HTTP status {status}"], False
        return [], False
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


def expected_error(expect, error):
    """Whether the recipe expects this navigation error: the figure is Chrome's error page."""
    pattern = (expect or {}).get("error")
    return bool(pattern and error and re.search(pattern, error))


def lookup(host, agent, timeout=20):
    """What public DNS says about `host`: its response code, and its IPv4 and IPv6 addresses."""
    found = {"rcode": None, "addresses": []}
    for kind, number in (("A", 1), ("AAAA", 28)):
        query = urllib.parse.urlencode({"name": host, "type": kind})
        request = urllib.request.Request(f"{DOH}?{query}",
                                         headers={"User-Agent": agent, "Accept": "application/dns-json"})
        with urllib.request.urlopen(request, timeout=timeout) as r:
            answer = json.load(r)
        found["rcode"] = found["rcode"] or RCODES.get(answer.get("Status"), str(answer.get("Status")))
        found["addresses"] += [a["data"] for a in answer.get("Answer") or [] if a.get("type") == number]
    return found


def dead_host(dns):
    """Whether public DNS has no address for a host.

    Behind the session's proxy, a host whose name no longer resolves and a host
    the proxy refuses both reach Chrome as ERR_TUNNEL_CONNECTION_FAILED. Only the
    first may be photographed as a dead host. The second is a policy, to report.
    """
    return bool(dns) and not dns.get("addresses")
