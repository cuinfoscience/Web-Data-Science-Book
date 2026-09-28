"""Evidence: the queries behind a number or a claim in a caption (AAR P1-2).

A recipe lists them under a figure's `evidence:`:

    evidence:
      - id: x-com-images
        claim: "six of the page's seven images were captured only as 404s"
        url: https://web.archive.org/cdx/search/cdx
        params: {url: 'x.com/images/', matchType: prefix, output: json, fl: 'urlkey,timestamp,statuscode',
                 filter: 'urlkey:.*/(main_x|spacer)\\.gif$', limit: 1000, showResumeKey: 'true'}
        page: resume_key          # follow the CDX resume key until the API stops returning one
        summary: {group_by: urlkey, count: statuscode}

`tools/shots/run evidence ch-07` runs each query as the captures load pages:
with the figure's User-Agent, 8-30 seconds between requests to one host, and
retries after a 5xx or a dropped connection. It pages until the query is
exhausted and saves every response under out/. A query is complete only if its
last page said so: a CDX page without a resume key, or, with `page: none`,
fewer rows than `limit`. A page that returns exactly `limit` rows with no way
to page fails. That check would have caught week 7's first account of x.com's
broken images, a 25-row answer to a query with more.

A complete run is recorded in images/<chapter>/provenance.json, under
`evidence`: each request, its rows, the total, the date, and the summary.
`check` warns about a figure whose recipe lists evidence with no complete
record, or with a record of an older version of the query or its claim.

Summaries, over the rows (CDX JSON: a header row, then one row per capture):

    summary: {group_by: urlkey, count: statuscode}   {urlkey: {statuscode: rows}}, and each urlkey's
                                                     first and last timestamps
    summary: {runs: statuscode}                      consecutive rows with one value, in the
                                                     API's order: [value, first timestamp, last, rows]
"""
import datetime
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request

from .env import OUT, rel

KEYS = {"id", "claim", "url", "params", "page", "summary"}
PAGING = {"resume_key", "none"}
SUMMARIES = {"group_by", "count", "runs"}
MAX_PAGES = 200


class EvidenceError(Exception):
    pass


def problems(evidence):
    """Recipe problems with a figure's `evidence:` list."""
    out = []
    if not isinstance(evidence, list):
        return ["`evidence` is a list of queries"]
    seen = set()
    for n, q in enumerate(evidence, 1):
        where = f"evidence {n}"
        if not isinstance(q, dict):
            out.append(f"{where}: not a mapping")
            continue
        out += [f"{where}: unknown key `{k}`" for k in set(q) - KEYS]
        for key in ("id", "claim", "url"):
            if not isinstance(q.get(key), str) or not q[key].strip():
                out.append(f"{where}: needs `{key}`")
        if q.get("id") in seen:
            out.append(f"{where}: duplicate id `{q['id']}`")
        seen.add(q.get("id"))
        if q.get("page", "none") not in PAGING:
            out.append(f"{where}: `page` is one of {sorted(PAGING)}")
        params = q.get("params") or {}
        if not isinstance(params, dict):
            out.append(f"{where}: `params` is a mapping")
            params = {}
        if q.get("page") == "resume_key" and str(params.get("showResumeKey", "")).lower() != "true":
            out.append(f"{where}: `page: resume_key` needs `showResumeKey: 'true'` in `params`")
        if "limit" not in params:
            out.append(f"{where}: set `limit` in `params`, so a page that hits it can be told from a "
                       "complete answer")
        summary = q.get("summary") or {}
        out += [f"{where}: unknown summary `{k}`" for k in set(summary) - SUMMARIES]
        if ("group_by" in summary) != ("count" in summary):
            out.append(f"{where}: a summary's `group_by` and `count` go together")
    return out


def query_sha256(q):
    """The query as the API sees it, and how it is summarized: a record of another version is stale."""
    text = json.dumps({k: q.get(k) for k in ("url", "params", "page", "summary")}, sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()


def _get(url, agent, timeout):
    request = urllib.request.Request(url, headers={"User-Agent": agent})
    with urllib.request.urlopen(request, timeout=timeout) as r:
        return r.status, r.read()


def _fetch(url, agent, timeout, retries, say):
    """(status, body), retrying a 5xx or a dropped connection after the toolkit's backoff."""
    from .capture import BACKOFF
    for n in range(retries + 1):
        if n:
            wait = BACKOFF[min(n - 1, len(BACKOFF) - 1)]
            say(f"    waiting {wait}s before try {n + 1}")
            time.sleep(wait)
        try:
            return _get(url, agent, timeout)
        except urllib.error.HTTPError as e:
            if e.code >= 500 and n < retries:
                say(f"    HTTP {e.code}; will retry")
                continue
            raise EvidenceError(f"HTTP {e.code} from {url}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if n < retries:
                say(f"    {str(getattr(e, 'reason', e))}; will retry")
                continue
            raise EvidenceError(f"no answer from {url}: {getattr(e, 'reason', e)}")
    raise EvidenceError(f"no answer from {url}")


def _rows(body):
    """A CDX JSON page: (header, rows, resume key or None)."""
    try:
        data = json.loads(body or b"[]")
    except ValueError:
        raise EvidenceError("the answer is not JSON (set `output: json` in `params`)")
    if not isinstance(data, list):
        raise EvidenceError("the answer is not a JSON list of rows")
    resume = None
    if len(data) >= 2 and data[-2] == [] and len(data[-1]) == 1:
        resume, data = data[-1][0], data[:-2]
    if not data:
        return [], [], resume
    return data[0], data[1:], resume


def summarize(summary, header, rows):
    out = {}
    index = {name: i for i, name in enumerate(header)}
    missing = [f for f in (summary.get("group_by"), summary.get("count"), summary.get("runs")) if f and f not in index]
    if missing:
        raise EvidenceError(f"the rows have no field {', '.join(missing)} (add it to `fl`)")
    if "group_by" in summary:
        g, c, t = index[summary["group_by"]], index[summary["count"]], index.get("timestamp")
        groups, first, last = {}, {}, {}
        for row in rows:
            counts = groups.setdefault(row[g], {})
            counts[row[c]] = counts.get(row[c], 0) + 1
            if t is not None:
                first[row[g]] = min(first.get(row[g], row[t]), row[t])
                last[row[g]] = max(last.get(row[g], row[t]), row[t])
        out["groups"] = {k: dict(sorted(v.items())) for k, v in sorted(groups.items())}
        if first:
            out["first"], out["last"] = dict(sorted(first.items())), dict(sorted(last.items()))
    if "runs" in summary:
        v, t = index[summary["runs"]], index.get("timestamp")
        runs = []
        for row in rows:
            stamp = row[t] if t is not None else None
            if runs and runs[-1][0] == row[v]:
                runs[-1][2], runs[-1][3] = stamp, runs[-1][3] + 1
            else:
                runs.append([row[v], stamp, stamp, 1])
        out["runs"] = runs
    return out


def run(chapter, fig, q, pacer=None, say=print):
    """Run one query to its end; returns its record, or raises EvidenceError."""
    if pacer is None:
        from .capture import Pacer
        pacer = Pacer()
    params = {k: str(v) for k, v in (q.get("params") or {}).items()}
    limit = int(params["limit"])
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder = OUT / chapter / fig["id"] / "evidence" / f"{stamp}-{q['id']}"
    folder.mkdir(parents=True, exist_ok=True)
    requests, header, rows, resume = [], None, [], None
    for n in range(MAX_PAGES):
        page_params = dict(params, **({"resumeKey": resume} if resume else {}))
        url = q["url"] + "?" + urllib.parse.urlencode(page_params)
        paced = pacer.wait(url, fig["pause"])
        status, body = _fetch(url, fig["user_agent"], fig["timeout"] * 3, fig["retries"], say)
        (folder / f"page-{n + 1}.json").write_bytes(body)
        head, got, resume = _rows(body)
        if header is None:
            header = head
        elif head and head != header:
            raise EvidenceError(f"page {n + 1}'s fields ({head}) differ from page 1's ({header})")
        rows += got
        requests.append({"url": url, "status": status, "rows": len(got), "paced_seconds": round(paced, 1),
                         **({"resume_key": resume} if resume else {})})
        say(f"    page {n + 1}: {len(got)} row(s){', and a resume key' if resume else ''}")
        if q.get("page") == "resume_key" and resume:
            continue
        if resume:
            raise EvidenceError(f"page {n + 1} came back with a resume key: more rows wait, and the query "
                                "doesn't follow them (`page: resume_key`)")
        if len(got) >= limit:
            raise EvidenceError(f"page {n + 1} returned exactly its limit ({limit} rows) and the query can't "
                                "page: the answer may be cut short. Page with `page: resume_key` "
                                "(and `showResumeKey: 'true'`), or raise `limit` until it isn't reached")
        break
    else:
        raise EvidenceError(f"still paging after {MAX_PAGES} pages; narrow the query")
    record = {
        "id": q["id"], "claim": q["claim"], "url": q["url"], "params": params, "page": q.get("page", "none"),
        "query_sha256": query_sha256(q), "complete": True,
        "fetched": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "user_agent": fig["user_agent"], "requests": requests, "rows": len(rows), "fields": header or [],
        "responses": rel(folder),
    }
    if q.get("summary"):
        record["summary"] = summarize(q["summary"], header or [], rows)
    (folder / "record.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def stale(fig, recorded):
    """Problems with a figure's recorded evidence against its recipe, one line each."""
    out = []
    have = {e.get("id"): e for e in recorded or []}
    for q in fig.get("evidence") or []:
        e = have.get(q["id"])
        if not e:
            out.append(f"evidence `{q['id']}` has not been run (tools/shots/run evidence {fig['chapter']} "
                       f"--only {fig['id']})")
        elif not e.get("complete"):
            out.append(f"evidence `{q['id']}` is recorded as incomplete")
        elif e.get("query_sha256") != query_sha256(q):
            out.append(f"evidence `{q['id']}`: the query changed after it was run on {e.get('fetched', '')[:10]}")
        elif e.get("claim") != q["claim"]:
            out.append(f"evidence `{q['id']}`: the claim changed after the query ran; run it again, and read "
                       "its summary against the new claim")
    for eid in set(have) - {q["id"] for q in fig.get("evidence") or []}:
        out.append(f"evidence `{eid}` is recorded, but the recipe no longer lists it")
    return out

