""















import glob
import json
import math
import os
import re
import stat
import time

FILE_NAME = "coop-session-summary.json"

MAX_CHARS = 1900

MAX_FILE_BYTES = 64 * 1024
SCHEMAS = (1,)

RUNNING_S = 75
MAX_PROBLEMS = 5
NORMAL_STEPS = 83


HEALTH_KEYS = (("physics_x", 100), ("physics_ms", 1000), ("app_ms", 1000), ("in_kbs", 100000), ("out_kbs", 100000),
               ("loss_per_s", 10000), ("holds_per_s", 100000), ("backlog_ms", 100000), ("refused_per_s", 100000),
               ("mem_used_gb", 10000), ("mem_free_gb", 10000), ("mem_total_gb", 10000))

TITLE = "Bug reporting"


HINT = "The launcher gathers the technical details. Describe what happened in the form or post."
CHOICE = "Same report either way. GitHub needs a free account; Discord doesn't."
GITHUB_LABEL = "Report on GitHub"
DISCORD_LABEL = "Post on Discord"
COPY_LABEL = "Copy to clipboard"

AFTER_GITHUB = "The report is copied: paste it into the Launcher report box."
AFTER_DISCORD = ("The report is copied: make a new post in #bug-reports and paste it. New to the server? Accept the "
                 "rules in #rules first.")
PASTE_NOTE = "Each button copies the report and opens your browser. Nothing is sent from your PC."
NO_SESSION = "No co-op session found yet. The report still lists the versions."




DISCLAIMER = ("About this report: it holds technical details of your latest co-op session only (versions, host or "
              "client, connection type, ping, performance and counts of problems). It excludes names, Steam IDs, IP "
              "addresses, passwords and file paths. Read it before sharing it. The tool does not upload it; you "
              "choose whether and where to paste it. What you write in the form or the post is public. It is used "
              "only to diagnose and troubleshoot bugs in the co-op mod.")

_FOLDER = re.compile(r"(HostSaves|ClientSaves)(-instance\d{1,2})?", re.I)
_MOD = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}")
_BUILD = re.compile(r"[0-9a-f]{7,12}\+?|unknown")
_GAME = re.compile(r"V ?\d\.\d{1,2}(\.\d{1,2}){1,3}[a-z]?")
_CODE = re.compile(r"[a-z][a-z_]{0,23}")



CODES = frozenset("""
admission aggro attitude bindings bite bodies bodypark charcreate charsync combatsfx
companions containers crashlog deadmarker demowin dialoguegate dialoguesync doors exits
game gamelock gather gatherfade gatherfreeze gatherhide gatherscreen golemsrv
grab guard guiskin health healthicons hitacct hitburst hooks hostile hostilehud hostthrottle hudgate
interlock inventory_guard invsync itemids items joinveil kinesis knockout kocopy leave
levelgate liveatk livewpn localcoop logging lurch memory menu menunotice menurejoin
migrants multiinst netplay nodeindex nopause objects pad party partyfx perf
phystrap pitclean plates playerrec players pose power privacy progress progstore
puppetsleep rejoin reports resolver savexfer sessionsum simgrid spawn spells srctime
startroom steamfriends steaminvite steamnet stephitch strikes summon swing torchfx
touchpoints trace transition travel veilhud worldid worldops wounds
""".split())
EXTRA_CODES = frozenset(("plugin", "net", "other"))
ROLES = ("host", "client", "solo")
CONNECTIONS = {"direct": "direct", "steam": "Steam relay", "direct+steam": "direct and Steam", "none": None}
LEVELS = {"warn": "warning", "error": "error"}




def summary_paths(appdata=None):
    ""
    appdata = appdata if appdata is not None else os.environ.get("APPDATA", "")
    if not appdata:
        return []
    base = os.path.join(appdata, "ExanimaCoop")
    out = []
    for pattern in ("HostSaves*", "ClientSaves*"):
        for d in sorted(glob.glob(os.path.join(glob.escape(base), pattern))):
            name = os.path.basename(d)
            if _FOLDER.fullmatch(name):
                out.append(("host" if name.lower().startswith("host") else "client", os.path.join(d, "Exanima", FILE_NAME)))
    return out


def newest_summary(appdata=None):
    ""
    best = None
    for kind, p in summary_paths(appdata):
        try:
            st = os.stat(p)
        except OSError:
            continue
        if not stat.S_ISREG(st.st_mode):
            continue
        if best is None or st.st_mtime > best[2]:
            best = (kind, p, st.st_mtime)
    return best


def read_summary(path):
    ""
    try:
        with open(path, "rb") as f:
            data = f.read(MAX_FILE_BYTES + 1)
    except (OSError, ValueError):
        return None
    if len(data) > MAX_FILE_BYTES:
        return None
    try:
        obj = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, RecursionError):
        return None
    return obj if isinstance(obj, dict) else None




def _int(v, lo, hi):
    if isinstance(v, bool) or not isinstance(v, int):
        return None
    return v if lo <= v <= hi else None


def _num(v, lo, hi):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    v = float(v)
    return v if math.isfinite(v) and lo <= v <= hi else None


def _str(v, rx):
    return v if isinstance(v, str) and len(v) <= 24 and rx.fullmatch(v) else None


def _word(v, words):
    return v if isinstance(v, str) and v in words else None


def facts(summary, info=None, age_s=None):
    ""

    info = info if isinstance(info, dict) else {}
    f = {"have_summary": False}
    s = summary if isinstance(summary, dict) and _int(summary.get("schema"), 0, 10 ** 6) in SCHEMAS else None
    src = s or {}
    f["mod"] = _str(src.get("mod"), _MOD) or _str(info.get("mod_version"), _MOD)
    f["build"] = _str(src.get("build"), _BUILD) or _str(info.get("build"), _BUILD)
    f["game"] = _str(src.get("game"), _GAME) or _str(info.get("game_version"), _GAME)
    f["protocol"] = _int(src.get("protocol"), 1, 65535) or _int(info.get("protocol"), 1, 65535)
    f["preview"] = src.get("build_kind") == "dev"
    f["age_s"] = _num(age_s, 0, 10 ** 10)
    if s is None:
        return f
    f["have_summary"] = True
    f["role"] = _word(s.get("role"), ROLES)
    f["players"] = _int(s.get("players_max"), 1, 64)
    conn = _word(s.get("connection"), CONNECTIONS)
    f["connection"] = CONNECTIONS.get(conn) if conn else None
    f["ping"] = _int(s.get("ping_ms"), 1, 2000)
    f["session_s"] = _int(s.get("session_s"), 0, 30 * 24 * 3600)
    f["level"] = _int(s.get("level"), 1, 100000)
    f["levels_seen"] = _int(s.get("levels_seen"), 0, 64)
    f["phys_s"] = _num(s.get("phys_s"), 0, 30 * 24 * 3600)
    f["steps"] = _num(s.get("phys_steps_per_s"), 0, 10000)
    f["ms_step"] = _num(s.get("phys_ms_per_step"), 0, 10000)
    f["slow_pct"] = _num(s.get("phys_slow_pct"), 0, 100)
    f["cpus"] = _int(s.get("cpus"), 1, 1024)
    hl = s.get("health")
    if isinstance(hl, dict):
        h = {k: _num(hl.get(k), 0, hi) for k, hi in HEALTH_KEYS}
        f["health"] = h if all(v is not None for v in h.values()) else None
    counts = {}
    raw = s.get("problems")
    if isinstance(raw, list):
        for p in raw[:256]:
            if not isinstance(p, dict):
                continue
            code, level, n = _str(p.get("code"), _CODE), _word(p.get("level"), LEVELS), _int(p.get("n"), 1, 10 ** 9)
            if code and level and n:
                if code not in CODES and code not in EXTRA_CODES:
                    code = "other"
                counts[(code, level)] = min(10 ** 9, counts.get((code, level), 0) + n)
    f["problems"] = [(c, l, n) for (c, l), n in counts.items()]
    f["log_skipped"] = s.get("log_skipped") is True
    f["sc_ok"] = _int(s.get("selfcheck_ok"), 0, 100000)
    f["sc_total"] = _int(s.get("selfcheck_total"), 0, 100000)
    f["sc_moved"] = _int(s.get("selfcheck_moved"), 0, 100000)
    f["startup_problems"] = _int(s.get("startup_problems"), 0, 100000)
    if s.get("crashed") is True:
        f["crash"] = "yes"
    elif s.get("clean_exit") is True:
        f["crash"] = "no"
    elif age_s is not None and 0 <= age_s < RUNNING_S:
        f["crash"] = "unknown (the game may still be running)"
    else:
        f["crash"] = "likely (the game did not close normally)"
    return f




def _q(v, fmt="%s"):
    return fmt % v if v is not None else "?"


def _minutes(sec):
    if sec is None:
        return "?"
    if sec < 60:
        return "under 1 min"
    m = sec // 60
    return "%d min" % m if m < 120 else "%d h %d min" % (m // 60, m % 60)


def problems_line(f):
    probs = sorted(f.get("problems") or [], key=lambda p: (p[1] != "error", -p[2], p[0]))
    if not probs:
        text = "none"
    else:
        shown = ["%s %s x%d" % (code.replace("_", " "), LEVELS[level], n) for code, level, n in probs[:MAX_PROBLEMS]]
        text = ", ".join(shown)
        if len(probs) > MAX_PROBLEMS:
            text += ", +%d more" % (len(probs) - MAX_PROBLEMS)
    if f.get("log_skipped"):
        text += " (counts are a minimum)"
    return "Problems seen: " + text


def selfcheck_text(f):
    ok, total, moved, sp = f.get("sc_ok"), f.get("sc_total"), f.get("sc_moved"), f.get("startup_problems")
    if not total:
        text = "not run"
    elif not moved and not sp:
        text = "ok (%d/%d)" % (ok or 0, total)
    else:
        parts = ["%d/%d ok" % (ok or 0, total)]
        if moved:
            parts.append("%d moved" % moved)
        if sp:
            parts.append("%d of the problems at start-up" % sp)
        text = ", ".join(parts)
    return "Self-check: %s | crash last session: %s" % (text, f.get("crash") or "?")


def health_line(h):
    ""
    text = "Health (latest): physics %.2fx %.2f ms, app %.1f ms | line in %d KB/s out %d KB/s, loss %.1f/s, holds %d/s, backlog %d ms, refused %d/s" % (
        h["physics_x"], h["physics_ms"], h["app_ms"], h["in_kbs"], h["out_kbs"], h["loss_per_s"], h["holds_per_s"], h["backlog_ms"], h["refused_per_s"])
    if h["mem_total_gb"] > 0:
        text += " | memory %.1f GB used, %.1f free of %.1f GB" % (h["mem_used_gb"], h["mem_free_gb"], h["mem_total_gb"])
    return text


def head_lines(f):
    ""
    build = f.get("build")
    tag = ", preview build" if f.get("preview") else ""
    build_part = " (build %s%s)" % (build, tag) if build else (" (preview build)" if tag else "")
    lines = ["Unofficial Exanima Multiplayer Mod report",
             "Mod %s%s | Game %s | Protocol %s" % (_q(f.get("mod")), build_part, _q(f.get("game")), _q(f.get("protocol")))]
    if not f.get("have_summary"):
        lines.append("Session: no co-op session found")
        return lines
    conn = "Connection: %s" % (f.get("connection") or "none")
    if f.get("ping") and f.get("connection"):
        conn += ", ping ~%d ms" % f["ping"]
    lines.append("Role: %s | Players: %s | %s" % (_q(f.get("role")), _q(f.get("players")), conn))
    level = "map %d" % f["level"] if f.get("level") else "none"
    if f.get("level") and (f.get("levels_seen") or 0) > 1:
        level += " (%d levels this session)" % f["levels_seen"]
    age = age_text(f.get("age_s"))
    lines.append("Session: %s%s | Level: %s" % (_minutes(f.get("session_s")), " (summary from %s)" % age if age else "", level))
    if f.get("steps") is not None and f.get("ms_step") is not None and (f.get("phys_s") or 0) >= 10:
        phys = "Physics: %.1f steps/s (normal ~%d; avg %.2f ms/step)" % (f["steps"], NORMAL_STEPS, f["ms_step"])
        if f.get("slow_pct") is not None and f["slow_pct"] >= 1:
            phys += " | slow motion %d%% of the time" % round(f["slow_pct"])
    else:
        phys = "Physics: not measured (no level played)"
    if f.get("cpus"):
        phys += " | %d CPU threads" % f["cpus"]
    lines.append(phys)
    if f.get("health"):
        lines.append(health_line(f["health"]))
    lines.append(problems_line(f))
    lines.append(selfcheck_text(f))
    return lines


def age_text(age_s):
    ""
    if age_s is None or age_s < 0:
        return ""
    if age_s < 120:
        return "just now"
    if age_s < 3600:
        return "%d min ago" % (age_s // 60)
    if age_s < 48 * 3600:
        return "%d h ago" % (age_s // 3600)
    return "%d days ago" % (age_s // 86400)


def build_text(f):
    ""
    return "\n".join(head_lines(f))


def _url_value(v):
    ""

    return "".join(c if c.isascii() and (c.isalnum() or c in "-._~") else "".join("%%%02X" % b for b in c.encode("utf-8"))
                   for c in v)


def issue_form_url(repo_url, f):
    ""


    if not repo_url:
        return None
    q = [("template", "bug.yml")]
    if f.get("mod"):
        q.append(("version", f["mod"]))
    if f.get("game"):
        q.append(("game", re.sub(r"^V ?", "", f["game"])))
    return repo_url.rstrip("/") + "/issues/new?" + "&".join("%s=%s" % (k, _url_value(v)) for k, v in q)


def source_line(f, kind, age_s):
    ""
    if not f.get("have_summary"):
        return NO_SESSION
    role = f.get("role") or kind or "co-op"
    ago = ""
    if age_s is not None and age_s >= 0:
        if age_s < RUNNING_S and f.get("crash", "").startswith("unknown"):
            ago = ", still running"
        elif age_s < 3600:
            ago = ", last updated %d min ago" % max(1, int(age_s // 60))
        elif age_s < 48 * 3600:
            ago = ", last updated %d h ago" % int(age_s // 3600)
        else:
            ago = ", last updated %d days ago" % int(age_s // 86400)
    return "From your latest session (%s, %s%s)." % (role, _minutes(f.get("session_s")), ago)


def load(info=None, appdata=None, now=None):
    ""
    try:
        found = newest_summary(appdata)
    except OSError:
        found = None
    summary, kind, age = None, None, None
    if found:
        kind, path, mtime = found
        summary = read_summary(path)
        age = (now if now is not None else time.time()) - mtime
    f = facts(summary, info, age)
    return f, source_line(f, kind, age)
