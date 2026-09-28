"""Where things live, the proxy, and the browser the toolkit drives."""
import json
import os
import subprocess
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent      # tools/shots
ROOT = TOOL.parent.parent                          # the textbook repository
# The three folders can be moved (selftest.py points them at a temporary tree).
RECIPES = Path(os.environ.get("SHOTS_RECIPES", TOOL / "recipes"))
OUT = Path(os.environ.get("SHOTS_OUT", TOOL / "out"))          # takes and logs; git-ignored
IMAGES = Path(os.environ.get("SHOTS_IMAGES", ROOT / "images"))

# Chrome for Testing, pinned by major version so DevTools and rendering stay put.
CHROME_VERSION = os.environ.get("SHOTS_CHROME_VERSION", "154")


def proxy():
    """The HTTPS proxy every request must go through, or None."""
    return os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")


def selenium_manager():
    try:
        import selenium
    except ImportError:
        return None
    base = Path(selenium.__file__).parent / "webdriver" / "common"
    for sub in ("linux-x86_64", "linux", "macos"):
        path = base / sub / "selenium-manager"
        if path.exists():
            return path
    return None


def chrome_path():
    """Chrome for Testing at the pinned version; Selenium Manager downloads it once."""
    if os.environ.get("SHOTS_CHROME"):
        return os.environ["SHOTS_CHROME"]
    manager = selenium_manager()
    if manager is None:
        raise RuntimeError("selenium is not installed; run  bash tools/shots/bootstrap.sh")
    env = dict(os.environ, SE_SKIP_DRIVER_IN_PATH="true")
    run = subprocess.run([str(manager), "--browser", "chrome", "--browser-version", CHROME_VERSION,
                          "--output", "json"], capture_output=True, text=True, env=env, timeout=900)
    try:
        return json.loads(run.stdout)["result"]["browser_path"]
    except (ValueError, KeyError):
        raise RuntimeError(f"Selenium Manager could not provide Chrome for Testing {CHROME_VERSION}:\n"
                           f"{run.stdout[-600:]}{run.stderr[-600:]}")


def chrome_version(path):
    run = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=60)
    return run.stdout.strip() or "unknown"


def playwright_version():
    try:
        from importlib.metadata import version
        return version("playwright")
    except Exception:
        return "unknown"


def rel(path):
    """A path relative to the repository, for messages and records."""
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)
