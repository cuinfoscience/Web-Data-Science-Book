#!/usr/bin/env bash
# Set up everything tools/shots needs in a fresh container. Safe to re-run:
# each step checks first and says what it did.
#
#   bash tools/shots/bootstrap.sh            headless capture (milestone M1)
#   bash tools/shots/bootstrap.sh --headed   also the virtual display and input tools (M2)
#   bash tools/shots/bootstrap.sh --tex      also TeX, for drawing markers (M3)
#   bash tools/shots/bootstrap.sh --headed --tex
#
# It never disables certificate checks, never unsets the proxy, and never runs
# `playwright install` (this environment provides browsers another way).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$HERE/.venv"
CHROME_VERSION="${SHOTS_CHROME_VERSION:-154}"
HEADED=0
TEX=0
for arg in "$@"; do
  case "$arg" in
    --headed) HEADED=1 ;;
    --tex) TEX=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

say() { printf '  %s\n' "$*"; }

echo "tools/shots bootstrap"

# 1. System packages, only what is missing.
need=()
command -v certutil >/dev/null || need+=(libnss3-tools)
if [[ $HEADED == 1 ]]; then
  command -v Xvfb >/dev/null || need+=(xvfb)
  command -v xdotool >/dev/null || need+=(xdotool)
  command -v import >/dev/null || need+=(imagemagick)
fi
if [[ $TEX == 1 ]]; then
  # pdflatex with TikZ, the standalone class, and Helvetica; pdftocairo
  command -v pdflatex >/dev/null || need+=(texlive-latex-base)
  kpsewhich tikz.sty >/dev/null 2>&1 || need+=(texlive-pictures)
  kpsewhich standalone.cls >/dev/null 2>&1 || need+=(texlive-latex-extra)
  kpsewhich helvet.sty >/dev/null 2>&1 || need+=(texlive-fonts-recommended)
  command -v pdftocairo >/dev/null || need+=(poppler-utils)
fi
# (Read the font list once: `fc-list | grep -q` fails under pipefail when grep stops early.)
FONTS="$(fc-list 2>/dev/null || true)"
grep -qi "Noto Sans" <<<"$FONTS" || need+=(fonts-noto-core)
grep -qi "DejaVu Sans" <<<"$FONTS" || need+=(fonts-dejavu-core)   # composite labels, contact sheets
if ((${#need[@]})); then
  say "installing: ${need[*]}"
  if command -v apt-get >/dev/null; then
    SUDO=""; [[ $(id -u) != 0 ]] && SUDO="sudo"
    $SUDO apt-get update -qq >/dev/null
    $SUDO apt-get install -y -qq --no-install-recommends "${need[@]}" >/dev/null
  else
    say "no apt-get here; install these yourself: ${need[*]}"
  fi
else
  say "system packages: present"
fi

# 2. Python packages, pinned, in a virtual environment of their own.
if [[ ! -x "$VENV/bin/python" ]]; then
  python3 -m venv "$VENV"
  say "created $VENV"
fi
"$VENV/bin/python" -m pip install -q --disable-pip-version-check -r "$HERE/requirements.txt"
say "python packages: $("$VENV/bin/python" -m pip freeze | grep -iE '^(playwright|selenium|pyyaml|pillow)==' | tr '\n' ' ')"

# 3. Chrome for Testing at the pinned major version, via Selenium Manager.
SM="$("$VENV/bin/python" - <<'EOF'
import pathlib, selenium
base = pathlib.Path(selenium.__file__).parent / "webdriver" / "common"
for sub in ("linux-x86_64", "linux", "macos"):
    p = base / sub / "selenium-manager"
    if p.exists():
        print(p); break
EOF
)"
CHROME="$(SE_SKIP_DRIVER_IN_PATH=true "$SM" --browser chrome --browser-version "$CHROME_VERSION" --output json \
  | "$VENV/bin/python" -c 'import json,sys; print(json.load(sys.stdin)["result"]["browser_path"])')"
say "browser: $("$CHROME" --version 2>/dev/null) at $CHROME"

# 4. Chrome trusts the proxy's certificate authority (Chrome reads the NSS store,
#    not the system bundle). Add it only if it is missing.
CA="${SHOTS_PROXY_CA:-/root/.ccr/agent-proxy-ca.crt}"
if [[ -n "${HTTPS_PROXY:-}" && -f "$CA" ]]; then
  DB="sql:$HOME/.pki/nssdb"
  mkdir -p "$HOME/.pki/nssdb"
  [[ -f "$HOME/.pki/nssdb/cert9.db" ]] || certutil -d "$DB" -N --empty-password
  if certutil -d "$DB" -L 2>/dev/null | grep -q "shots-proxy-ca\|agent-proxy\|ccr"; then
    say "proxy CA: already trusted by Chrome"
  else
    certutil -d "$DB" -A -t "C,," -n shots-proxy-ca -i "$CA"
    say "proxy CA: added to Chrome's certificate store"
  fi
else
  say "proxy CA: no HTTPS_PROXY or no CA file at $CA; skipping"
fi

echo "done. Next: tools/shots/run doctor"
