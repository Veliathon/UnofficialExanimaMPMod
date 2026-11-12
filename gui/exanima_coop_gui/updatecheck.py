""













import json
import os
import re
import subprocess

API_HOST = "api.github.com"
API_PATH = "/repos/Veliathon/UnofficialExanimaMPMod/releases/latest"
LATEST_URL = "https://" + API_HOST + API_PATH
RELEASES_URL = "https://github.com/Veliathon/UnofficialExanimaMPMod/releases"
USER_AGENT = "UEMM-launcher"
TIMEOUT_S = 5
MAX_BYTES = 1_000_000
CREATE_NO_WINDOW = 0x08000000
_VERSION = re.compile(r"^\d+(\.\d+){0,3}$")


def curl_path(env=None):
    ""
    env = os.environ if env is None else env
    return os.path.join(env.get("SystemRoot") or env.get("SYSTEMROOT") or r"C:\Windows", "System32", "curl.exe")


def command(curl):
    ""

    return [curl, "-q", "--silent", "--fail", "--max-time", str(TIMEOUT_S), "--proto", "=https", "--max-filesize", str(MAX_BYTES),
            "--user-agent", USER_AGENT, "--header", "Accept: application/vnd.github+json", LATEST_URL]


def fetch(run=None, curl=None):
    ""
    run = run or subprocess.run
    curl = curl or curl_path()
    if not os.path.isfile(curl):
        return None
    try:
        r = run(command(curl), capture_output=True, timeout=TIMEOUT_S + 2, creationflags=CREATE_NO_WINDOW)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    if r.returncode != 0 or not r.stdout:
        return None
    return bytes(r.stdout[:MAX_BYTES])


def version_key(v):
    ""
    v = (v or "").strip()
    if v[:1] in ("v", "V"):
        v = v[1:]
    if not _VERSION.match(v):
        return None
    return tuple(int(x) for x in v.split("."))


def is_newer(latest, ours):
    ""
    a, b = version_key(latest), version_key(ours)
    if a is None or b is None:
        return False
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)) > b + (0,) * (n - len(b))


def parse_latest(body):
    ""

    try:
        d = json.loads(body.decode("utf-8") if isinstance(body, (bytes, bytearray)) else body)
    except (ValueError, TypeError, AttributeError, UnicodeDecodeError):
        return None
    if not isinstance(d, dict) or d.get("draft") or d.get("prerelease"):
        return None
    tag = d.get("tag_name")
    if not isinstance(tag, str) or version_key(tag) is None:
        return None
    version = tag.strip().lstrip("vV")
    date = d.get("published_at") if isinstance(d.get("published_at"), str) else ""
    notes = d.get("body") if isinstance(d.get("body"), str) else ""
    name = d.get("name") if isinstance(d.get("name"), str) else ""
    return {"version": version, "date": date[:10], "notes": notes, "name": name}


def check(our_version, enabled, fetch=fetch):
    ""

    if not enabled or version_key(our_version) is None:
        return None
    body = fetch()
    if not body:
        return None
    latest = parse_latest(body)
    return latest if latest and is_newer(latest["version"], our_version) else None


def banner(latest):
    ""
    return "%s is out." % latest["version"]
