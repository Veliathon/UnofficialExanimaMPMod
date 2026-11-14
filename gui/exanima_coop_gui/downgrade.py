""






































import datetime
import ntpath
import os

POLL_MS = 2000


STABLE_POLLS = 3

GROWTH_WINDOW_S = 30.0

CLICK_SLACK_S = 5.0


REPLACED_SLACK_S = 60.0



BUTTON = "Open Steam console"
COPY = "Copy"
COPY_AGAIN = "Copy again"
INSTRUCTION = "In Steam's console, click into the box at the bottom, press Ctrl+V to paste, then press Enter."

IDLE = "Nothing downloaded yet."
WAITING = "Now in Steam's console: press Ctrl+V, then Enter."
RETRY = "To try again, click %s, then paste in Steam's console again: Ctrl+V, then Enter." % BUTTON
NEXT_IDLE = "Start with step 1: click %s below." % BUTTON
NEXT_IDLE_UPDATE = ("Update Exanima in Steam: this window notices it by itself. Or start with step 1: click %s below."
                    % BUTTON)
NEXT_WAITING = ("Steam's console is a text window inside Steam. It can take a moment to open and may be behind this "
                "window: look in Steam. Click into the box at its bottom, press Ctrl+V, then Enter. Pasted something "
                "else? Click %s below, then paste once more." % COPY_AGAIN)
NEXT_DOWNLOADING = ("Nothing to do now: keep Steam open and wait. This window tells you when it's ready, and the "
                    "button below changes to Install the mod into it.")
NEXT_READY = "Last step: click Install the mod into it below."
NEXT_BLOCKED = "Close what uses it, then click %s again." % BUTTON
NEXT_FAILED = RETRY + " Steam must be signed in to the account that owns Exanima, with enough free disk space."
NEXT_NOT_REPLACED = ("Click %s again: it first moves the old copy aside (nothing is deleted). Then paste in "
                     "Steam's console again: Ctrl+V, then Enter." % BUTTON)

STEP_OF = {"ready": 4, "blocked": 1, "mismatch": 1, "idle": 1, "not_replaced": 1, "failed": 1, "waiting": 2, "downloading": 3}



VERIFY = "in your Steam Library, right-click Exanima > Properties > Installed Files > Verify integrity of game files"


def update_first(installed):
    ""


    return (installed or {}).get("age") in ("older", "changed")


def _yours(installed):
    ""
    parts = [installed.get("version") or ""]
    if installed.get("buildid"):
        parts.append("Steam build %s" % installed["buildid"])
    return ", ".join(p for p in parts if p)


def intro(expected, build, size_bytes, installed=None):
    ""


    head = "This co-op mod runs on exactly Exanima %s (Steam build %s). " % (expected, build)
    size = "about %.0f GB" % ((size_bytes or 8.4e9) / 1e9)
    inst = installed or {}
    yours = _yours(inst)
    yours = " (%s)" % yours if yours else ""
    second = ("Or follow the steps below: Steam downloads that version for free as a second copy (%s); your normal "
              "install stays as it is." % size)
    if inst.get("age") == "older":
        return head + ("Your Steam install is an older build%s. Update it through Steam: let Steam's update finish, or "
                       "%s (and if a beta is selected under Betas, choose None). This window notices it by itself. "
                       % (yours, VERIFY)) + second
    if inst.get("age") == "changed":
        return head + ("Your Steam install has that build, but its Exanima.exe was changed or is damaged. Repair it: %s. "
                       "This window notices it by itself. " % VERIFY) + second
    newer = ("Your Steam install is a newer build%s that this mod does not support yet. " % yours) if inst.get("age") == "newer" else ""
    return head + newer + ("Steam can download that version for free, as a second copy next to your normal install "
                           "(%s). Your normal Exanima install stays as it is." % size)


def heading(installed=None):
    ""
    return "Or get it as a second copy" if update_first(installed) else "How to get it"


def gate_sub(installed=None):
    ""
    if (installed or {}).get("age") == "older":
        return "Your Steam install is older: update it through Steam."
    return "The co-op mod needs exactly this game version."


def steps(expected, size_bytes):
    ""

    return [
        "Click %s below. This copies a download command and opens Steam's console (a text window inside Steam)." % BUTTON,
        "In that window, click into the box at the bottom, press Ctrl+V to paste, then press Enter.",
        "Steam downloads Exanima %s (about %.0f GB) in the background. This window watches the download and tells "
        "you when it's ready; nothing else to do." % (expected, (size_bytes or 8.4e9) / 1e9),
    ]


def current_step(phase):
    ""
    return STEP_OF.get(phase, 1)


def button_words(text):
    ""

    return (text or "").replace("click Downgrade", "click " + BUTTON).replace("Click Downgrade", "Click " + BUTTON)


def parse_log_time(s):
    ""
    try:
        return datetime.datetime.strptime((s or "").strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def gb(n):
    return "%.1f GB" % (n / 1e9)


def depot_bytes(status):
    ""

    sizes = [int(d.get("bytes") or 0) for d in (status.get("depots") or []) if d.get("exists")]
    return max(sizes) if sizes else None


def _dir_key(p):
    return (p or "").replace("/", "\\").rstrip("\\").lower()


def depot_newest(status, dir_=None):
    ""

    deps = [d for d in (status.get("depots") or []) if d.get("exists") and d.get("newest") is not None]
    named = [d for d in deps if dir_ and _dir_key(d.get("dir")) == _dir_key(dir_)]
    pick = named or deps
    if not pick:
        return None
    try:
        return datetime.datetime.fromtimestamp(max(int(d["newest"]) for d in pick))
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def files_replaced(status, ev):
    ""

    start = parse_log_time(ev.get("started")) or parse_log_time(ev.get("time"))
    newest = depot_newest(status, ev.get("dir"))
    if start is None or newest is None:
        return None
    return newest >= start - datetime.timedelta(seconds=REPLACED_SLACK_S)


def free_label(status):
    ""
    n = int(status.get("old_bytes") or 0) if status.get("ok") else 0
    return ("Free %s" % gb(n)) if (status.get("old") and n > 0) else None


class Watcher:
    def __init__(self, update=False):


        self.update = update
        self.clicked_at = None
        self.last_bytes = None
        self.grew_at = None
        self.stable = 0
        self.block = None

    def clicked(self, now):
        self.clicked_at = now
        self.block = None

    def blocked(self, text):
        ""

        self.block = button_words(text) or "The old copy could not be moved aside."
        self.clicked_at = None

    def _after_click(self, when):
        return self.clicked_at is not None and when is not None and when >= self.clicked_at - datetime.timedelta(seconds=CLICK_SLACK_S)

    def step(self, status, now):
        ""


        expected = status.get("expected") or "the supported version"
        clicked = self.clicked_at is not None
        if not status.get("ok"):

            if clicked:
                return self._out("waiting", WAITING, None, NEXT_WAITING)
            if self.block:
                return self._out("blocked", self.block, None, NEXT_BLOCKED)
            return self._out("idle", IDLE, None, NEXT_IDLE_UPDATE if self.update else NEXT_IDLE)

        size = depot_bytes(status)
        if size is not None:
            if self.last_bytes is not None and size > self.last_bytes:
                self.grew_at = now
            self.stable = self.stable + 1 if size == self.last_bytes else 0
            self.last_bytes = size
        growing = self.grew_at is not None and (now - self.grew_at).total_seconds() <= GROWTH_WINDOW_S

        ev = status.get("console") or {}
        kind = ev.get("kind")
        ev_time = parse_log_time(ev.get("time"))
        running = kind == "started"
        total = int(status.get("depot_size") or 0)

        sup = status.get("supported")
        if sup:
            whole = total and size is not None and size >= total and self.stable >= STABLE_POLLS

            busy = sup.get("source") == "steam_depot" and (running or growing) and not whole and kind != "complete"
            if not busy:
                return self._out("ready", "Exanima %s is ready%s." % (expected, _where(sup)), 1.0, NEXT_READY, sup)
            return self._downloading(size, total, ev)

        if running or (growing and clicked):
            return self._downloading(size, total, ev)
        if kind == "failed" and self._after_click(ev_time):
            return self._out("failed", "Steam stopped the download: %s." % (ev.get("text") or "no reason given"), None, NEXT_FAILED)
        if kind == "complete" and self._after_click(ev_time):


            replaced = files_replaced(status, ev)
            if ev.get("ours") is False:
                text = "Steam downloaded a different version (manifest %s)." % ev.get("manifest")
            elif replaced is False:
                return self._out("not_replaced", "Steam finished, but the files weren't replaced.", None, NEXT_NOT_REPLACED)
            elif replaced:
                text = "Steam finished, but the files it wrote are not Exanima %s." % expected
            else:
                text = "Steam says the download is complete, but Exanima %s is not there." % expected
            return self._out("mismatch", text, None, RETRY)
        if clicked:
            return self._out("waiting", WAITING, None, NEXT_WAITING)
        if self.block:
            return self._out("blocked", self.block, None, NEXT_BLOCKED)
        return self._out("idle", IDLE, None, NEXT_IDLE_UPDATE if self.update else NEXT_IDLE)

    def _downloading(self, size, total, ev):
        if total and size is not None and 0 < size < total:
            return self._out("downloading", "Steam is downloading…  %s of %s" % (gb(size), gb(total)), size / total, NEXT_DOWNLOADING)
        mb = ev.get("mb") if ev.get("kind") == "started" else None
        extra = "%s" % gb(mb * 1e6) if mb else "several GB"
        return self._out("downloading", "Steam is downloading… (%s, this can take a while)" % extra, None, NEXT_DOWNLOADING)

    @staticmethod
    def _out(phase, text, progress, next_="", sup=None):
        return {
            "phase": phase,
            "text": text,
            "next": next_,
            "progress": progress,
            "ready_dir": (sup or {}).get("dir"),
            "ready_source": (sup or {}).get("source"),
        }


def _where(sup):
    return {
        "steam_depot": " (the Steam console download; your normal install is untouched)",
        "steam_common": " (your Steam install)",
        "launcher_dir": " (the launcher's folder)",
        "explicit": " (the game folder given to the launcher)",
    }.get(sup.get("source"), "")


def main_button(phase):
    ""



    return "install" if phase == "ready" else "downgrade"


def move_aside_first(phase):
    ""

    return phase != "downloading"


def prepare_outcome(r):
    ""

    if r is None:
        return True, None
    if r.get("ok"):
        return True, r.get("text") or None
    return False, button_words(r.get("text") or r.get("error")) or "The old copy could not be moved aside."




def folder_target(path, isdir=os.path.isdir):
    ""


    p = (path or "").strip().strip('"').strip()
    if not p:
        return None
    p = ntpath.normpath(p)
    try:
        return p if isdir(p) else None
    except (OSError, ValueError):
        return None


def _explorer(path):
    os.startfile(path)


def open_folder(path, opener=None, isdir=os.path.isdir):
    ""
    target = folder_target(path, isdir)
    if target is None:
        return False
    try:
        (opener or _explorer)(target)
    except OSError:
        return False
    return True
