""








import os
import re

BUNDLED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsnew.md")
TITLE = "What's new"
MISSING = "The release notes come with the release package; this copy of the launcher has none."
CHECK_LABEL = "Check for updates"
CHECK_TIP = "Opens the releases page in your browser."
DOWNLOAD_LABEL = "Download"
DOWNLOAD_TIP = "Opens the releases page in your browser. The launcher downloads nothing itself."
SETTING_LABEL = "Check GitHub for new versions"
SETTING_TIP = "The launcher asks GitHub once at start whether a newer version exists. Nothing else is sent."
MAX_CHARS = 40_000


def read_bundled(path=None):
    ""
    try:
        with open(path or BUNDLED, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_EMPH = re.compile(r"(\*\*|__|`)")


def inline(text):
    ""
    return _EMPH.sub("", _LINK.sub(r"\1", text)).strip()


_ALERT = re.compile(r"^\[!(CAUTION|WARNING)\]$", re.I)
_BOLD_LINE = re.compile(r"^(\*\*|__)(.+)\1$")


def parse(md, limit=MAX_CHARS):
    ""



    md = re.sub(r"<!--.*?-->", "", (md or "")[:limit], flags=re.S)
    blocks = []
    cur = None
    alert = False
    for raw in md.replace("\r\n", "\n").split("\n"):
        line = raw.rstrip()
        s = line.strip()
        if s.startswith(">"):
            q = s[1:].strip()
            if _ALERT.match(q):
                alert, cur = True, None
                continue
            if not q:
                cur = None
                continue
            kind = "caution" if alert else "text"
            if alert and _BOLD_LINE.match(q):
                blocks.append(["caution_title", inline(q)])
                cur = None
            elif cur is not None and cur[0] == kind:
                cur[1] = (cur[1] + " " + inline(q)).strip()
            else:
                cur = [kind, inline(q)]
                blocks.append(cur)
            continue
        if alert:
            alert, cur = False, None
        if not s:
            cur = None
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            blocks.append(("title" if len(m.group(1)) == 1 else "heading", inline(m.group(2))))
            cur = None
            continue
        m = re.match(r"^[-*+]\s+(.*)$", s)
        if m and not line.startswith("    "):
            cur = ["bullet", inline(m.group(1))]
            blocks.append(cur)
            continue
        if cur is not None and (cur[0] == "text" or line.startswith(" ")):
            cur[1] = (cur[1] + " " + inline(s)).strip()
            continue
        cur = ["text", inline(s)]
        blocks.append(cur)
    return [(k, t) for k, t in (tuple(b) for b in blocks) if t]
