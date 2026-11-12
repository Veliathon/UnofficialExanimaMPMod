""













import tkinter as tk
from tkinter import ttk

from . import __version__
from . import about as AB
from . import theme as T
from .theme import px
from .widgets import RoundButton, RoundFrame

SETTINGS_KEY = "notice_seen"
WAIT_S = 10
OK = "OK"
QUIT = "Quit"
TITLE = "Please read: a note for players"

LINES = (
    ("para", "This is an unofficial, fan-made multiplayer mod. What you are about to play is an altered version of "
             "Exanima, not the game as its developer made it, so it does not represent the original game. Issues you "
             "run into may come from the mod rather than the game."),
    ("para", "Exanima is a carefully crafted single-player game. Ideally, play this mod only once you have properly "
             "enjoyed the original on its own: it is the best way to see the care and detail its developer put in, "
             "and then to enjoy it together with friends."),
    ("para", "While the mod is installed or was in use:"),
    ("item", "please do not contact Bare Mettle Entertainment about any problem;"),
    ("item", "please do not post bugs or issues on the official Exanima forums, Steam discussions or Bare Mettle's "
             "channels;"),
    ("item", "report everything to us instead: click the bug icon in the launcher (GitHub Issues or our Discord)."),
    ("para", "The \"UEMM\" mark in the corner of the screen and the line under the menu logo show that the mod is "
             "running. Please leave them visible in screenshots and videos, so nobody mistakes the mod for the "
             "original game."),
)


def seen(settings, version=__version__):
    ""
    return (settings or {}).get(SETTINGS_KEY) == version


def needs_notice(settings, version=__version__, bypass=False, force=False):
    ""

    if force:
        return True
    if bypass:
        return False
    return not seen(settings, version)


def seed(settings, version=__version__):
    ""
    settings[SETTINGS_KEY] = version
    return settings


def ok_label(left):
    ""
    return "%s (%d)" % (OK, left) if left > 0 else OK


class NoticeGate(tk.Frame):
    ""



    def __init__(self, parent, on_ok, on_quit, wait_s=WAIT_S):
        super().__init__(parent, bg=T.BG)
        self.on_ok = on_ok
        self.on_quit = on_quit
        self.left = wait_s
        self._after = None
        tk.Label(self, text=AB.PRODUCT_NAME, bg=T.BG, fg=T.ACCENT, font=(T.FONT_TITLE, 16, "bold"),
                 anchor="w").pack(side="top", fill="x")
        tk.Label(self, text=TITLE, bg=T.BG, fg=T.MUTED, font=T.font(9), anchor="w",
                 justify="left").pack(side="top", fill="x", pady=(px(2), px(8)))
        foot = tk.Frame(self, bg=T.BG)
        foot.pack(side="bottom", fill="x", pady=(px(10), 0))
        self.ok_btn = RoundButton(foot, ok_label(self.left), self._ok, kind="primary", height=36, size=10)
        self.ok_btn.pack(side="right")
        self.quit_btn = RoundButton(foot, QUIT, self._quit, kind="secondary", height=36, size=10)
        self.quit_btn.pack(side="right", padx=(0, px(8)))
        card = RoundFrame(self, pad=10)
        card.pack(side="top", fill="both", expand=True)
        self.text = tk.Text(card.inner, bg=T.SURFACE, fg=T.TEXT, font=T.font(10), wrap="word", relief="flat", bd=0,
                            highlightthickness=0, padx=px(6), pady=px(4), cursor="arrow", width=1, height=1,
                            selectbackground=T.ACCENT_LO, selectforeground=T.ON_ACCENT, insertwidth=0, takefocus=0)
        bar = ttk.Scrollbar(card.inner, orient="vertical", style="Dark.Vertical.TScrollbar", command=self.text.yview)
        self.text.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y", padx=(px(6), 0))
        self.text.pack(side="left", fill="both", expand=True)
        self._fill()
        self.text.bind("<MouseWheel>", lambda e: (self.text.yview_scroll(int(-e.delta / 120) or (-1 if e.delta > 0 else 1), "units"), "break")[1])
        self._tick()

    def _fill(self):
        t = self.text
        gap = px(8)
        t.tag_configure("para", spacing3=gap)
        t.tag_configure("item", lmargin1=px(10), lmargin2=px(22), spacing3=px(3))
        for kind, line in LINES:
            t.insert("end", ("•  " + line if kind == "item" else line) + "\n", kind)
        t.configure(state="disabled")

    def _tick(self):
        ""
        self._after = None
        self.ok_btn.configure_button(text=ok_label(self.left), enabled=self.left <= 0)
        if self.left > 0:
            self.left -= 1
            self._after = self.after(1000, self._tick)

    def _ok(self):
        if self.left <= 0:
            self.on_ok()

    def _quit(self):
        self.on_quit()

    def destroy(self):
        if self._after is not None:
            try:
                self.after_cancel(self._after)
            except tk.TclError:
                pass
            self._after = None
        super().destroy()
