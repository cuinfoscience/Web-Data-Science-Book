"""What a host's robots.txt says about a figure's page.

`doctor ch-NN` reads each host's robots.txt for the capture's own User-Agent,
the course's, and also for the names Anthropic's agents go by. The course's
User-Agent decides (docs/decisions.md, 2026-09-24); a group addressed only to
Claude's agents is reported as a note, so it stays visible. The Guardian's and
www.bbc.co.uk's files, for example, allow the course's User-Agent (it falls
under `*`) and disallow Claude's agents.
"""
import urllib.robotparser

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
