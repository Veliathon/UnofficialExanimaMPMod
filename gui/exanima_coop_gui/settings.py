""

















import json
import os
import re

from . import secret

PASSWORD_KEYS = ("host_password", "join_password")

BACKGROUNDS = ("unknown", "villager", "proctor", "host")



NAME_MAX = 15


NAME_POOL = ["Aldric", "Cedric", "Edmund", "Godric", "Osric", "Roland"]
DEFAULT_FRIEND_NAMES = NAME_POOL[:3]


def next_default_name(used):
    ""
    taken = {(u or "").strip().lower() for u in used}
    for n in NAME_POOL:
        if n.lower() not in taken:
            return n
    k = 1
    while "friend %d" % k in taken:
        k += 1
    return "Friend %d" % k


def body_name_problem(names, i):
    ""

    n = (names[i] or "").strip()
    if not n:
        return "A name is required."
    if len(n) > NAME_MAX:
        return "At most %d characters." % NAME_MAX
    if "," in n or not all(" " <= c <= "~" for c in n):
        return "Letters, digits, spaces and simple punctuation only (no commas)."
    if any((m or "").strip().lower() == n.lower() for m in names[:i]):
        return "Two friends can't share the name %s." % n
    return None












LAUNCHER_NAME_MAX = 15
LAUNCHER_NAME_PUNCT = "-_.'"
FALLBACK_NAME = "Player"
PROBLEM_FONT = "The game's font has only Western European letters (A-Z, accented letters like é ü ß ø)."
PROBLEM_CHARS = "Letters, digits, spaces and - _ . ' only."


def latin1_letter(c):
    ""
    return "À" <= c <= "ÿ" and c not in "×÷"


def name_letter_or_digit(c):
    return (c.isascii() and c.isalnum()) or latin1_letter(c)


def launcher_name_char_ok(c):
    return name_letter_or_digit(c) or c == " " or c in LAUNCHER_NAME_PUNCT


def _composed(text):
    ""


    try:
        import unicodedata
    except ImportError:
        return text
    return unicodedata.normalize("NFC", text)


def clean_name(name):
    ""

    return _composed(name or "").strip()


def launcher_name_problem(name):
    ""


    n = clean_name(name)
    if not n:
        return "Type your name: the host and your friends see it."
    bad = [c for c in n if not launcher_name_char_ok(c)]
    if any(c.isalnum() for c in bad):
        return PROBLEM_FONT
    if bad:
        return PROBLEM_CHARS
    if len(n) > LAUNCHER_NAME_MAX:
        return "At most %d characters (the game's name field)." % LAUNCHER_NAME_MAX
    if not any(name_letter_or_digit(c) for c in n):
        return "Use at least one letter or digit."
    if "  " in n:
        return "No double spaces."
    return None


def sanitize_launcher_name(raw):
    ""


    out = ""
    for c in _composed(raw or ""):
        if not launcher_name_char_ok(c):
            continue
        if c == " " and (not out or out.endswith(" ")):
            continue
        if len(out) >= LAUNCHER_NAME_MAX:
            break
        out += c
    out = out.strip()
    return FALLBACK_NAME if launcher_name_problem(out) else out






GUI_SLOTS_MAX = 4
_gui_slot_handle = None
_gui_slot = None


def gui_slot_mutex_name(n):
    return "Local\\ExanimaCoop.Gui.%d" % n


def claim_gui_slot():
    ""



    global _gui_slot
    if _gui_slot is None:
        _gui_slot = _claim_free_slot()
    return _gui_slot


def _claim_free_slot():
    global _gui_slot_handle
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        k32.CreateMutexW.restype = wintypes.HANDLE
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
    except (ImportError, OSError, AttributeError, ValueError):
        return 1
    for n in range(1, GUI_SLOTS_MAX + 1):
        ctypes.set_last_error(0)
        h = k32.CreateMutexW(None, False, gui_slot_mutex_name(n))
        if not h:
            return 1
        if ctypes.get_last_error() == 183:
            k32.CloseHandle(h)
            continue
        _gui_slot_handle = h
        return n
    return 1


def first_free_slot(held):
    ""



    held = list(held)[:GUI_SLOTS_MAX]
    for n in range(1, GUI_SLOTS_MAX + 1):
        if n > len(held) or not held[n - 1]:
            return n
    return 1


def held_gui_slots():
    ""

    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenMutexW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
        k32.OpenMutexW.restype = wintypes.HANDLE
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
    except (ImportError, OSError, AttributeError, ValueError):
        return [False] * GUI_SLOTS_MAX
    out = []
    for n in range(1, GUI_SLOTS_MAX + 1):
        h = k32.OpenMutexW(0x00100000, False, gui_slot_mutex_name(n))
        if h:
            k32.CloseHandle(h)
        out.append(bool(h))
    return out


def name_key(slot):
    ""
    return "name" if slot <= 1 else "name_%d" % slot


NAME_KEYS = tuple(name_key(n) for n in range(1, GUI_SLOTS_MAX + 1))


def default_slot_name(first, slot):
    ""


    if slot <= 1:
        return first
    base = (first or "").strip()
    cand = "%s %d" % (base, slot)
    return cand if base and launcher_name_problem(cand) is None else "%s %d" % (FALLBACK_NAME, slot)


def slot_name(s, slot):
    ""


    own = s.get(name_key(slot)) or ""
    if own.strip():
        return own
    return default_slot_name(s.get("name") or "", slot)


def merge_other_names(s, disk, slot):
    ""

    for key in NAME_KEYS:
        if key != name_key(slot):
            s[key] = disk.get(key, "")
    return s


DEFAULTS = {
    "mode": "host",

    "route": "steam",

    "update_check": True,
    "name": "",

    "name_2": "",
    "name_3": "",
    "name_4": "",
    "last_ip": "",
    "players": 2,
    "friends_start_as": "unknown",

    "friend_names": list(DEFAULT_FRIEND_NAMES),
    "friend_types": ["unknown", "unknown", "unknown"],
    "show_console": True,
    "remember_password": False,

    "demo_tile": False,


    "close_on_start": False,


    "detailed_logs": False,


    "open_port": False,



    "steam_access": "invite",
    "host_password": "",
    "join_password": "",


    "last_body": {},



    "licence_accepted": {},


    "notice_seen": "",


    "risk_ack": "",
}

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def clean_licence_record(raw):
    ""
    if isinstance(raw, dict) and isinstance(raw.get("sha256"), str) and _HEX64.match(raw["sha256"]):
        date = raw.get("date")
        return {"sha256": raw["sha256"], "date": date[:40] if isinstance(date, str) else ""}
    return {}


def settings_path():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "ExanimaCoop", "launcher.json")


def _clean(raw):
    ""
    s = dict(DEFAULTS)
    s["last_body"] = {}
    s["licence_accepted"] = {}
    s["friend_names"] = list(DEFAULT_FRIEND_NAMES)
    s["friend_types"] = ["unknown"] * 3
    if not isinstance(raw, dict):
        return s
    if raw.get("friends_start_as") in BACKGROUNDS:

        s["friend_types"] = [raw["friends_start_as"]] * 3
    fn = raw.get("friend_names")
    if isinstance(fn, list):
        for i, v in enumerate(fn[:3]):
            if isinstance(v, str):
                s["friend_names"][i] = v[:40]
    ft = raw.get("friend_types")
    if isinstance(ft, list):
        for i, v in enumerate(ft[:3]):
            if v in BACKGROUNDS:
                s["friend_types"][i] = v
    if raw.get("mode") in ("host", "join"):
        s["mode"] = raw["mode"]
    if raw.get("route") in ("steam", "manual"):
        s["route"] = raw["route"]
    if isinstance(raw.get("update_check"), bool):
        s["update_check"] = raw["update_check"]
    for key in ("name", "name_2", "name_3", "name_4", "last_ip", "host_password", "join_password"):
        if isinstance(raw.get(key), str):
            s[key] = raw[key][:200]
    p = raw.get("players")
    if isinstance(p, int) and not isinstance(p, bool) and 1 <= p <= 4:
        s["players"] = p
    if raw.get("friends_start_as") in BACKGROUNDS:
        s["friends_start_as"] = raw["friends_start_as"]
    if raw.get("steam_access") in ("friends", "invite"):
        s["steam_access"] = raw["steam_access"]
    for key in ("show_console", "remember_password", "demo_tile", "close_on_start", "detailed_logs", "open_port"):
        if isinstance(raw.get(key), bool):
            s[key] = raw[key]
    lb = raw.get("last_body")
    if isinstance(lb, dict):

        s["last_body"] = {str(k): v.strip()[:40] for k, v in lb.items() if isinstance(v, str) and v.strip()}
    s["licence_accepted"] = clean_licence_record(raw.get("licence_accepted"))
    if isinstance(raw.get("notice_seen"), str):
        s["notice_seen"] = raw["notice_seen"][:40]
    if isinstance(raw.get("risk_ack"), str):
        s["risk_ack"] = raw["risk_ack"][:40]
    if not s["remember_password"]:
        s["host_password"] = ""
        s["join_password"] = ""
    return s


def load(path=None):
    ""



    path = path or settings_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, ValueError):
        return _clean({})
    s = _clean(raw)
    if not isinstance(raw, dict):
        return s
    for key in PASSWORD_KEYS:
        plain = s[key]
        s[key] = ""
        if not s["remember_password"]:
            continue
        blob = raw.get(key + "_dpapi")
        if isinstance(blob, str) and blob:
            s[key] = secret.unprotect(blob)[:200]
        elif plain:
            s[key] = plain
    if any(isinstance(raw.get(k), str) and raw[k] for k in PASSWORD_KEYS):


        save(s, path)
    return s


def _to_disk(data):
    ""

    out = dict(data)
    for key in PASSWORD_KEYS:
        pw = out[key]
        out[key] = ""
        blob = secret.protect(pw) if (out["remember_password"] and pw) else ""
        out[key + "_dpapi"] = blob or ""
    return out


def save(settings, path=None):
    ""

    path = path or settings_path()
    data = _to_disk(_clean(settings))
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        os.replace(tmp, path)
        return path
    except OSError:
        return None
