"""What a host's robots.txt says about a figure's page.

`doctor ch-NN` reads each host's robots.txt twice over: for the capture's own
User-Agent, and for the names Anthropic's agents go by. A capture is made by
an AI agent working for the maintainer, so a rule addressed to those agents
applies to it whatever User-Agent the browser sends. In chapter 4's back-fill,
the Guardian's and www.bbc.co.uk's robots.txt files allowed the capture's
User-Agent (it falls under `*`) and disallowed Claude's agents; neither site
has a figure.
"""
import urllib.robotparser

# The names in robots.txt that address Anthropic's agents.
CLAUDE_AGENTS = ("Claude-User", "ClaudeBot", "Claude-SearchBot", "Claude-Web", "anthropic-ai")


def barred(text, agent, url):
    """The agents that robots.txt `text` disallows from `url`: the capture's `agent`, then Claude's."""
    robots = urllib.robotparser.RobotFileParser()
    robots.parse(text.splitlines())
    return [name for name in (agent,) + CLAUDE_AGENTS if not robots.can_fetch(name, url)]
