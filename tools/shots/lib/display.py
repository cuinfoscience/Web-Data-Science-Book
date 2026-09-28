"""A virtual X display (Xvfb) for headed captures, with real input and screen grabs.

The screen is sized from the window and the scale factor, plus a margin, so a
2x window is never cut off (it once was, before this toolkit). Input goes
through xdotool, so right-clicks, keys, and the pointer are real events that
the browser's own UI (context menus, DevTools, tooltips) responds to.
"""
import os
import shutil
import subprocess
import time
from pathlib import Path

MARGIN = 100


class DisplayError(Exception):
    pass


class Display:
    def __init__(self, width, height):
        for tool in ("Xvfb", "xdotool", "import"):
            if not shutil.which(tool):
                raise DisplayError(f"{tool} is missing; run  bash tools/shots/bootstrap.sh --headed")
        self.size = (width + MARGIN, height + MARGIN)
        self.number = next(n for n in range(90, 200) if not Path(f"/tmp/.X{n}-lock").exists())
        self.name = f":{self.number}"
        self.proc = subprocess.Popen(
            ["Xvfb", self.name, "-screen", "0", f"{self.size[0]}x{self.size[1]}x24", "-nolisten", "tcp"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 15
        while not Path(f"/tmp/.X11-unix/X{self.number}").exists():
            if self.proc.poll() is not None or time.monotonic() > deadline:
                raise DisplayError(f"Xvfb did not start on {self.name}")
            time.sleep(0.1)

    @property
    def env(self):
        return {**os.environ, "DISPLAY": self.name}

    def fits(self, width, height):
        return width + MARGIN <= self.size[0] and height + MARGIN <= self.size[1]

    def xdo(self, *args):
        subprocess.run(["xdotool", *[str(a) for a in args]], env=self.env, check=True,
                       capture_output=True, timeout=30)

    def grab(self, path):
        subprocess.run(["import", "-display", self.name, "-window", "root", str(path)],
                       check=True, capture_output=True, timeout=60)

    def close(self):
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
