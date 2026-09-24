"""What a host's robots.txt says about a figure's page.

`doctor ch-NN` reads each host's robots.txt for the capture's own User-Agent,
the course's, and also for the names Anthropic's agents go by. The course's
User-Agent decides (docs/decisions.md, 2026-09-24); a group addressed only to
Claude's agents is reported as a note, so it stays visible. The Guardian's and
www.bbc.co.uk's files, for example, allow the course's User-Agent (it falls
under `*`) and disallow Claude's agents.

A figure of an API's response, the request a chapter's own code makes, is
captured as an API client even where robots.txt disallows it (the decision of
2026-09-24): its recipe says `api_client: true`, and the disallow is a note.
"""
import urllib.robotparser
from urllib.parse import urlparse

# The names in robots.txt that address Anthropic's agents.
CLAUDE_AGENTS = ("Claude-User", "ClaudeBot", "Claude-SearchBot", "Claude-Web", "anthropic-ai")


def _parsed(text):
    robots = urllib.robotparser.RobotFileParser()
    robots.parse(text.splitlines())
    return robots


def barred(text, agent, url):
    """The agents that robots.txt `text` disallows from `url`: the capture's `agent`, then Claude's."""
    robots = _parsed(text)
    return [name for name in (agent,) + CLAUDE_AGENTS if not robots.can_fetch(name, url)]


def crawl_delay(text, agent):
    """The seconds robots.txt asks `agent` to leave between requests, or None."""
    delay = _parsed(text).crawl_delay(agent)
    return float(delay) if delay is not None else None


def findings(host, text, agent, pages):
    """What `doctor` says about each page: [(level, message, fix)], level "warn" or "note".

    `pages` is [(figure id, url, api_client)]. A page robots.txt disallows for the
    capture's User-Agent is a warning, unless it is an API's response.
    """
    out = []
    for fid, url, api_client in pages:
        page = url.removeprefix("view-source:")
        path = urlparse(page).path
        names = barred(text, agent, page)
        if agent in names and api_client:
            out.append(("note", f"{host}: robots.txt disallows {path} ({fid}), an API's response captured "
                                "as an API client", "docs/decisions.md, 2026-09-24"))
        elif agent in names:
            out.append(("warn", f"{host}: robots.txt disallows {path} ({fid})",
                        "leave the figure out, or ask the maintainer; an API's response takes `api_client: true`"))
        claude = [name for name in names if name != agent]
        if claude and agent not in names:
            out.append(("note", f"{host}: robots.txt disallows {path} for {', '.join(claude)} ({fid})",
                        "captures send the course's User-Agent, which it allows (docs/decisions.md, 2026-09-24)"))
    return out
