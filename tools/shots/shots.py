#!/usr/bin/env python3
"""Capture, check, and record the book's screenshots. See tools/shots/README.md.

    tools/shots/run doctor [ch-NN]            can this session capture? (run first, every time)
    tools/shots/run list [ch-NN]              recipes, approved images, and takes
    tools/shots/run capture ch-NN [--only ID ...]
    tools/shots/run compare ch-NN ID          newest take against the approved image
    tools/shots/run promote ch-NN ID [--take PATH]
    tools/shots/run adopt ch-NN [--only ID ...]   record provenance for images made before tools/shots
    tools/shots/run check [ch-NN ...]         recipes, provenance, and the chapter's figure blocks
    tools/shots/run status                    every figure's kind and age
    tools/shots/run clean [ch-NN]             delete old takes
    tools/shots/run selftest                  offline test of the guards and promote
"""
import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import provenance as prov                                      # noqa: E402
from lib.capture import Pacer, PolicyBlock, capture, sha256, takes      # noqa: E402
from lib.compare import compare                                         # noqa: E402
from lib.env import IMAGES, OUT, ROOT, TOOL, chrome_path, chrome_version, proxy, rel  # noqa: E402
from lib.recipes import DEFAULTS, RecipeError, chapters, figure, load   # noqa: E402

GOOD, WARN, BAD = "ok", "warn", "FAIL"


def line(mark, text, fix=None):
    print(f"  {mark:4}  {text}")
    if fix:
        print(f"        -> {fix}")


# ---------------------------------------------------------------- doctor
def cmd_doctor(args):
    failed = False
    print("Session")
    px = proxy()
    if px:
        try:
            # Ask the proxy itself, directly: this request must not be proxied.
            direct = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            direct.open(px.rstrip("/") + "/__agentproxy/status", timeout=10).read()
            line(GOOD, f"proxy {px} answers")
        except Exception as e:
            line(WARN, f"proxy {px} is set, but its status endpoint did not answer ({e})")
    else:
        line(GOOD, "no HTTPS_PROXY: requests go direct")
    try:
        path = chrome_path()
        line(GOOD, f"browser: {chrome_version(path)}")
    except Exception as e:
        line(BAD, f"no browser: {e}", "bash tools/shots/bootstrap.sh")
        return 1
    try:
        from lib.browser import Browser
        browser = Browser()
        context = browser.context({**DEFAULTS, "scale": 1})
        page = context.new_page()
        response = page.goto("https://example.com/", wait_until="domcontentloaded", timeout=60000)
        OUT.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(OUT / "doctor.png"))
        title = page.title()
        context.close()
        browser.close()
        if response and response.status == 200 and "Example Domain" in title:
            line(GOOD, "headless capture of https://example.com/ works")
        else:
            failed = True
            line(BAD, f"example.com answered {response and response.status} with title {title!r}")
    except Exception as e:
        failed = True
        error = str(e).splitlines()[0]
        if "ERR_CERT" in error:
            line(BAD, f"Chrome does not trust the proxy's certificate ({error})", "bash tools/shots/bootstrap.sh")
        elif "ERR_TUNNEL_CONNECTION_FAILED" in error:
            line(BAD, f"the proxy refused example.com ({error})",
                 "check the session's network policy; do not route around it")
        else:
            line(BAD, f"headless capture failed: {error}")
    missing = [t for t in ("Xvfb", "xdotool", "import") if not shutil.which(t)]
    if missing:
        line(WARN, f"headed capture needs {', '.join(missing)}, which is not installed",
             "bash tools/shots/bootstrap.sh --headed")
    else:
        failed |= doctor_headed()
    for chapter in args.chapters:
        failed |= doctor_chapter(chapter)
    print("Ready to capture." if not failed else "Not ready; fix the FAIL lines first.")
    return 1 if failed else 0


def doctor_headed():
    """A real headed window on the virtual display, with DevTools, grabbed from the screen."""
    from PIL import Image, ImageStat
    from lib import headed
    from lib.browser import Browser
    browser = None
    try:
        browser = Browser()
        fig = {**DEFAULTS, "id": "doctor", "chapter": "doctor", "mode": "headed", "scale": 1,
               "window": [900, 600], "devtools": {"dock": "right"}, "timeout": 60}
        session = headed.Session(browser, fig, browser.display(900, 600))
        try:
            response = session.page.goto("https://example.com/", wait_until="domcontentloaded", timeout=60000)
            session.ready()
            OUT.mkdir(parents=True, exist_ok=True)
            session.grab(OUT / "doctor-headed.png")
        finally:
            session.close()
        with Image.open(OUT / "doctor-headed.png") as img:
            spread = ImageStat.Stat(img.convert("L")).stddev[0]
        if response and response.status == 200 and spread > 3:
            line(GOOD, "headed capture works (virtual display, DevTools, screen grab)")
            return False
        line(BAD, f"headed capture of example.com came back wrong (status "
                  f"{response and response.status}, pixel spread {spread:.1f})")
    except Exception as e:
        line(BAD, f"headed capture failed: {str(e).splitlines()[0]}", "bash tools/shots/bootstrap.sh --headed")
    finally:
        if browser:
            browser.close()
    return True


def doctor_chapter(chapter):
    print(f"Hosts in {chapter}")
    failed = False
    recipe = load(chapter)
    by_host = {}
    for fig in recipe["figures"]:
        if fig.get("url") and host_of(fig["url"]):
            by_host.setdefault(host_of(fig["url"]), []).append(fig)
    for host, figs in sorted(by_host.items()):
        agent = figs[0]["user_agent"]
        request = urllib.request.Request(f"https://{host}/robots.txt", headers={"User-Agent": agent})
        try:
            with urllib.request.urlopen(request, timeout=30) as r:
                text = r.read().decode("utf-8", "replace")
            line(GOOD, f"{host}: reachable (robots.txt {r.status})")
        except urllib.error.HTTPError as e:
            line(GOOD if e.code in (404, 410) else WARN, f"{host}: robots.txt answered {e.code}")
            continue
        except Exception as e:
            reason = str(getattr(e, "reason", e))
            if "Tunnel connection failed" in reason:
                failed = True
                line(BAD, f"{host}: the proxy refused it ({reason})",
                     "a policy block: report it; do not retry or route around it")
            else:
                line(WARN, f"{host}: not reachable now ({reason})")
            continue
        robots = urllib.robotparser.RobotFileParser()
        robots.parse(text.splitlines())
        for fig in figs:
            page = fig["url"].removeprefix("view-source:")
            if not robots.can_fetch(agent, page):
                line(WARN, f"{host}: robots.txt disallows {urlparse(page).path} ({fig['id']})",
                     "one page view per figure; decide whether that fits the site's rules")
    return failed


def host_of(url):
    return urlparse(url.removeprefix("view-source:")).hostname


# ---------------------------------------------------------------- list / status
def cmd_list(args):
    for chapter in args.chapters or chapters():
        recipe = load(chapter)
        data = prov.load(chapter)
        print(f"{chapter}  ({rel(recipe['path'])}, {len(recipe['figures'])} figures)")
        for fig in recipe["figures"]:
            approved = "approved" if (IMAGES / chapter / fig["file"]).exists() else "no image"
            recorded = "recorded" if fig["id"] in data["figures"] else "no provenance"
            n = len(takes(chapter, fig["id"], ok_only=False))
            print(f"  {fig['id']:28} {fig['kind']:8} {fig['mode']:9} {approved}, {recorded}, {n} take(s)")
    return 0


def cmd_status(args):
    today = datetime.date.today()
    print(f"{'figure':38} {'kind':8} {'captured':10} {'age':>5}  recipe")
    for chapter in chapters():
        recipe = load(chapter)
        data = prov.load(chapter)
        for fig in recipe["figures"]:
            e = data["figures"].get(fig["id"])
            if not e:
                print(f"{chapter + '/' + fig['id']:38} {fig['kind']:8} {'-':10} {'-':>5}  no provenance")
                continue
            day = str(e.get("captured", ""))[:10]
            try:
                age = f"{(today - datetime.date.fromisoformat(day)).days}d"
            except ValueError:
                age = "?"
            same = e.get("recipe_sha256") == fig["recipe_sha256"]
            note = "same" if same else ("before tools/shots" if not e.get("recipe_sha256") else "changed since")
            print(f"{chapter + '/' + fig['id']:38} {e['kind']:8} {day:10} {age:>5}  {note}")
    return 0


# ---------------------------------------------------------------- capture / compare / promote
def cmd_capture(args):
    from lib.browser import Browser
    recipe = load(args.chapter)
    figs = [f for f in recipe["figures"] if not args.only or f["id"] in args.only]
    if args.only and len(figs) != len(set(args.only)):
        known = {f["id"] for f in recipe["figures"]}
        print(f"unknown figure(s): {', '.join(sorted(set(args.only) - known))}")
        return 2
    browser, pacer, bad, refused = Browser(), Pacer(), 0, set()
    try:
        for fig in figs:
            print(f"{args.chapter}/{fig['id']}")
            host = host_of(fig.get("url") or "")
            if host in refused:
                line(BAD, f"skipped: the proxy refused {host} earlier in this run")
                bad += 1
                continue
            try:
                take = capture(browser, fig, pacer, say=print)
            except PolicyBlock as e:
                refused.add(host)
                line(BAD, str(e), "a policy block: report it; do not retry or route around it")
                bad += 1
                continue
            if take.get("skipped"):
                line(WARN, take["skipped"])
            elif take["ok"]:
                line(GOOD, f"{take['image']}  ({take['size'][0]}x{take['size'][1]}, status {take['status']})")
                approved = IMAGES / args.chapter / fig["file"]
                if approved.exists():
                    c = compare(ROOT / take["image"], approved)
                    line(GOOD if c["similar"] else WARN,
                         f"against the approved image: distance {c['distance']}/64"
                         f"{'' if c['similar'] else ' - looks different; check it before promoting'}")
            else:
                bad += 1
                where = f" ({take['image']})" if take.get("image") else ""
                line(BAD, "; ".join(take["problems"]) + where)
    finally:
        browser.close()
    return 1 if bad else 0


def _take(args):
    if args.take:
        return json.loads(Path(args.take).with_suffix(".json").read_text())
    found = takes(args.chapter, args.id)
    return found[0] if found else None


def cmd_compare(args):
    fig = figure(load(args.chapter), args.id)
    take = _take(args)
    approved = IMAGES / args.chapter / fig["file"]
    if not take or not approved.exists():
        print("need a passing take and an approved image to compare")
        return 1
    c = compare(ROOT / take["image"], approved)
    print(json.dumps(c, indent=2))
    return 0 if c["similar"] else 1


def cmd_promote(args):
    recipe = load(args.chapter)
    fig = figure(recipe, args.id)
    take = _take(args)
    if not take:
        print(f"no passing take of {args.chapter}/{args.id}; run capture first")
        return 1
    if not take.get("ok"):
        print(f"refusing a take that failed its guards: {'; '.join(take.get('problems', []))}")
        return 1
    if take["recipe_sha256"] != fig["recipe_sha256"]:
        print("the recipe changed after this take; capture again")
        return 1
    source, target = ROOT / take["image"], IMAGES / args.chapter / fig["file"]
    if target.exists():
        c = compare(source, target)
        print(f"replacing {rel(target)} (distance {c['distance']}/64 from the old image)")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    data = prov.load(args.chapter)
    data["figures"][fig["id"]] = prov.from_take(take)
    prov.save(args.chapter, data)
    print(f"promoted {take['image']} -> {rel(target)}")
    print(prov.write_images_md(args.chapter, recipe["qmd"], data))
    return 0


def cmd_adopt(args):
    from PIL import Image
    recipe = load(args.chapter)
    data = prov.load(args.chapter)
    for fig in recipe["figures"]:
        if args.only and fig["id"] not in args.only:
            continue
        image = IMAGES / args.chapter / fig["file"]
        if not fig.get("legacy"):
            line(WARN, f"{fig['id']}: no `legacy:` block in the recipe")
        elif not image.exists():
            line(WARN, f"{fig['id']}: no image at {rel(image)}")
        elif fig["id"] in data["figures"] and not args.force:
            line(GOOD, f"{fig['id']}: already recorded")
        else:
            with Image.open(image) as img:
                size = list(img.size)
            data["figures"][fig["id"]] = prov.from_legacy(fig, sha256(image), size)
            line(GOOD, f"{fig['id']}: recorded ({fig['legacy']['captured']})")
    prov.save(args.chapter, data)
    print(prov.write_images_md(args.chapter, recipe["qmd"], data))
    return 0


# ---------------------------------------------------------------- check
def figure_block(qmd_text, chapter, file):
    pattern = re.compile(r"!\[(?P<caption>.*?)\]\(images/" + re.escape(f"{chapter}/{file}") +
                         r"\)\{(?P<attrs>[^}]*)\}")
    return pattern.search(qmd_text)


def cmd_check(args):
    errors = warnings = 0

    def err(text):
        nonlocal errors
        errors += 1
        line(BAD, text)

    def warn(text):
        nonlocal warnings
        warnings += 1
        line(WARN, text)

    for chapter in args.chapters or chapters():
        print(chapter)
        try:
            recipe = load(chapter)
        except RecipeError as e:
            err(str(e))
            continue
        data = prov.load(chapter)
        qmd = ROOT / recipe["qmd"] if recipe["qmd"] else None
        text = qmd.read_text() if qmd and qmd.exists() else ""
        ids = set()
        for fig in recipe["figures"]:
            ids.add(fig["id"])
            image = IMAGES / chapter / fig["file"]
            entry = data["figures"].get(fig["id"])
            if not image.exists():
                warn(f"{fig['id']}: no approved image yet")
                continue
            if not entry:
                err(f"{fig['id']}: {rel(image)} has no provenance (promote a take, or adopt it)")
            else:
                if entry.get("image_sha256") != sha256(image):
                    err(f"{fig['id']}: {rel(image)} changed after its provenance was recorded")
                if entry.get("kind") != fig["kind"]:
                    err(f"{fig['id']}: provenance says {entry.get('kind')}, recipe says {fig['kind']}")
            block = figure_block(text, chapter, fig["file"])
            if not block:
                warn(f"{fig['id']}: not used in {recipe['qmd']}")
                continue
            alt = re.search(r'fig-alt="([^"]*)"', block["attrs"])
            if not alt:
                err(f"{fig['id']}: the figure in {recipe['qmd']} has no fig-alt")
            elif len(alt.group(1)) < 80:
                warn(f"{fig['id']}: fig-alt is short ({len(alt.group(1))} characters)")
            year = str((entry or {}).get("captured", ""))[:4]
            if fig.get("drifts") and year and year not in block["caption"]:
                warn(f"{fig['id']}: shows things that change, but its caption doesn't say when "
                     f"it was captured (for example, 'in {year}')")
        for fid in set(data["figures"]) - ids:
            warn(f"provenance.json has `{fid}`, which no recipe describes")
        md = IMAGES / chapter / "IMAGES.md"
        if data["figures"]:
            current = md.read_text() if md.exists() else ""
            if prov.table(data) not in current:
                err(f"{rel(md)}: table out of date (run adopt or promote to rewrite it)")
    print(f"{errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


# ---------------------------------------------------------------- clean / selftest
def cmd_clean(args):
    removed = 0
    for chapter_dir in sorted(OUT.glob("ch-*")):
        if args.chapters and chapter_dir.name not in args.chapters:
            continue
        for fig_dir in sorted(p for p in chapter_dir.iterdir() if p.is_dir()):
            logs = sorted(fig_dir.glob("*.json"), reverse=True)
            keep = {logs[0]} if logs else set()
            newest_ok = next((p for p in logs if json.loads(p.read_text()).get("ok")), None)
            if newest_ok:
                keep.add(newest_ok)
            for log in logs:
                if log not in keep:
                    log.unlink()
                    log.with_suffix(".png").unlink(missing_ok=True)
                    removed += 1
    print(f"removed {removed} old take(s)")
    return 0


def cmd_selftest(args):
    return subprocess.run([sys.executable, str(TOOL / "selftest.py")]).returncode


def main():
    parser = argparse.ArgumentParser(prog="shots", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("doctor"); p.add_argument("chapters", nargs="*"); p.set_defaults(fn=cmd_doctor)
    p = sub.add_parser("list"); p.add_argument("chapters", nargs="*"); p.set_defaults(fn=cmd_list)
    p = sub.add_parser("status"); p.set_defaults(fn=cmd_status)
    p = sub.add_parser("capture"); p.add_argument("chapter"); p.add_argument("--only", nargs="+")
    p.set_defaults(fn=cmd_capture)
    for name, fn in (("compare", cmd_compare), ("promote", cmd_promote)):
        p = sub.add_parser(name); p.add_argument("chapter"); p.add_argument("id"); p.add_argument("--take")
        p.set_defaults(fn=fn)
    p = sub.add_parser("adopt"); p.add_argument("chapter"); p.add_argument("--only", nargs="+")
    p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_adopt)
    p = sub.add_parser("check"); p.add_argument("chapters", nargs="*"); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("clean"); p.add_argument("chapters", nargs="*"); p.set_defaults(fn=cmd_clean)
    p = sub.add_parser("selftest"); p.set_defaults(fn=cmd_selftest)
    args = parser.parse_args()
    try:
        return args.fn(args)
    except RecipeError as e:
        print(e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
