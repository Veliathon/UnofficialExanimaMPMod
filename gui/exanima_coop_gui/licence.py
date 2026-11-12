""












import datetime
import hashlib
import os
import re
import tkinter as tk
from tkinter import ttk

from . import about as AB
from . import settings as S
from . import theme as T
from .theme import px
from .widgets import RoundButton, RoundFrame

SETTINGS_KEY = "licence_accepted"
FILE_NAME = "LICENSE.txt"
MISSING = ("The licence file (LICENSE.txt) is missing from the mod's folder. Extract the whole download again, keeping "
           "every file together, then start the launcher again.")
INTRO = "Please read the licence. By choosing I agree, you accept it. We will ask again if the licence changes."
AGREE = "I agree"
QUIT = "Quit"


def candidates(here=None):
    ""

    here = os.path.abspath(here or os.path.dirname(os.path.abspath(__file__)))
    gui = os.path.dirname(here)
    top = os.path.dirname(gui)
    out = [os.path.join(top, FILE_NAME)]
    if os.path.basename(gui).lower() == "gui" and os.path.basename(top).lower() == "launcher":
        out.append(os.path.join(os.path.dirname(top), FILE_NAME))
    return out


def load_text(paths=None):
    ""
    for p in paths if paths is not None else candidates():
        try:
            with open(p, "r", encoding="utf-8-sig") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        if text.strip():
            return text
    return None


def normalise(text):
    ""

    lines = (text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(l.rstrip() for l in lines).strip("\n") + "\n"


def text_hash(text):
    ""
    return hashlib.sha256(normalise(text).encode("utf-8")).hexdigest()


def record(text, when=None):
    ""
    day = (when or datetime.date.today()).isoformat()
    return {"sha256": text_hash(text), "date": day}


def clean_record(raw):
    ""
    return S.clean_licence_record(raw)


def accepted(settings, text):
    ""
    if text is None:
        return False
    rec = clean_record((settings or {}).get(SETTINGS_KEY))
    return bool(rec) and rec["sha256"] == text_hash(text)


def needs_agreement(settings, text, bypass=False, force=False):
    ""

    if force:
        return True
    if bypass:
        return False
    return not accepted(settings, text)


def seed(settings, text=None):
    ""

    text = load_text() if text is None else text
    if text is not None:
        settings[SETTINGS_KEY] = record(text)
    return settings




_NUMBERED = re.compile(r"^\d{1,2}\.\s+\S.{0,60}$")
_END_PUNCT = ".,;:!?)]\""


def _is_heading(s):
    if s.startswith("- ") or s.startswith("["):
        return False
    if _NUMBERED.match(s):
        return True
    return len(s) < 60 and s[-1] not in _END_PUNCT


def reflow(text):
    ""





    lines = normalise(text).split("\n")
    width = max((len(l) for l in lines), default=0)
    long_line = max(40, width - 16)
    out = []
    prev_raw = None
    for raw in lines:
        s = raw.strip()
        if not s:
            prev_raw = None
            continue
        kind = out[-1][0] if out else None
        ends = prev_raw is None or len(prev_raw) < long_line or prev_raw.rstrip()[-1] in ".!?:]"
        if kind == "item":
            joins = prev_raw is not None and raw[:1].isspace()
        else:
            joins = kind == "para" and not ends and not s.startswith("- ") and not _NUMBERED.match(s)
        if joins:
            out[-1] = (kind, out[-1][1] + " " + s)
        elif s.startswith("- "):
            out.append(("item", s[2:]))
        elif prev_raw is None and s.upper() == s and len(s.split()) > 1 and any(c.isalpha() for c in s):
            out.append(("title", s))
        elif _is_heading(s) and ends:
            out.append(("heading", s))
        else:
            out.append(("para", s))
        prev_raw = raw
    return out




class LicenceGate(tk.Frame):
    ""



    def __init__(self, parent, text, on_agree, on_quit):
        super().__init__(parent, bg=T.BG)
        self.on_agree = on_agree
        self.on_quit = on_quit
        tk.Label(self, text=AB.PRODUCT_NAME, bg=T.BG, fg=T.ACCENT, font=(T.FONT_TITLE, 16, "bold"),
                 anchor="w").pack(side="top", fill="x")
        tk.Label(self, text=INTRO if text is not None else "Licence", bg=T.BG, fg=T.MUTED, font=T.font(9), anchor="w",
                 justify="left").pack(side="top", fill="x", pady=(px(2), px(8)))
        foot = tk.Frame(self, bg=T.BG)
        foot.pack(side="bottom", fill="x", pady=(px(10), 0))
        self.agree_btn = None
        if text is not None:
            self.agree_btn = RoundButton(foot, AGREE, self._agree, kind="primary", height=36, size=10)
            self.agree_btn.pack(side="right")
        self.quit_btn = RoundButton(foot, QUIT, self._quit, kind="secondary", height=36, size=10)
        self.quit_btn.pack(side="right", padx=(0, px(8)))
        card = RoundFrame(self, pad=10)
        card.pack(side="top", fill="both", expand=True)
        self.text = tk.Text(card.inner, bg=T.SURFACE, fg=T.TEXT, font=T.font(9), wrap="word", relief="flat", bd=0,
                            highlightthickness=0, padx=px(6), pady=px(4), cursor="arrow", width=1, height=1,
                            selectbackground=T.ACCENT_LO, selectforeground=T.ON_ACCENT, insertwidth=0, takefocus=0)
        bar = ttk.Scrollbar(card.inner, orient="vertical", style="Dark.Vertical.TScrollbar", command=self.text.yview)
        self.text.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y", padx=(px(6), 0))
        self.text.pack(side="left", fill="both", expand=True)
        self._fill(text)
        self.text.bind("<MouseWheel>", lambda e: (self.text.yview_scroll(int(-e.delta / 120) or (-1 if e.delta > 0 else 1), "units"), "break")[1])

    def _fill(self, text):
        t = self.text
        gap = px(6)
        t.tag_configure("title", font=T.font(10, "semibold"), foreground=T.TEXT, spacing3=gap)
        t.tag_configure("heading", font=T.font(10, "semibold"), foreground=T.ACCENT, spacing1=px(10), spacing3=px(2))
        t.tag_configure("para", spacing3=gap)
        t.tag_configure("item", lmargin1=px(10), lmargin2=px(22), spacing3=px(2))
        t.tag_configure("missing", foreground=T.ERROR, spacing3=gap)
        if text is None:
            t.insert("end", MISSING, "missing")
        else:
            for kind, line in reflow(text):
                t.insert("end", ("•  " + line if kind == "item" else line) + "\n", kind)
        t.configure(state="disabled")

    def _agree(self):
        self.on_agree()

    def _quit(self):
        self.on_quit()
