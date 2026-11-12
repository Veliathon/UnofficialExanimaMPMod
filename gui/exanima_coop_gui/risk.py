""













import tkinter as tk
from tkinter import ttk

from . import __version__
from . import about as AB
from . import theme as T
from .theme import px
from .widgets import RoundButton, RoundFrame

SETTINGS_KEY = "risk_ack"
CONTINUE = "I understand the risk, continue"
QUIT = "Quit"
TITLE = "WARNING: EXPERIMENTAL SOFTWARE, WRITTEN BY AI"
BODY = ("This mod's code was written by AI. Nobody can easily audit the whole code base, so its full behaviour, and "
        "what it might do to your PC, cannot be reviewed in total. The developer did ask AI to review it for safety, "
        "but that is AI checking its own work: not a real safety net. The mod runs inside the game and changes it "
        "while it plays. Use it entirely at your own risk. If you are not comfortable with that, do not download it "
        "and do not run it.")
DISCLAIMER = ("THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT "
              "LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO "
              "EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER "
              "IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR "
              "THE USE OR OTHER DEALINGS IN THE SOFTWARE.")
SEE_LICENCE = "See LICENSE.txt sections 9 and 10."


def acknowledged(settings, version=__version__):
    ""
    return (settings or {}).get(SETTINGS_KEY) == version


def needs_warning(settings, version=__version__, bypass=False, force=False):
    ""

    if force:
        return True
    if bypass:
        return False
    return not acknowledged(settings, version)


def seed(settings, version=__version__):
    ""
    settings[SETTINGS_KEY] = version
    return settings


class RiskGate(tk.Frame):
    ""



    def __init__(self, parent, on_continue, on_quit):
        super().__init__(parent, bg=T.BG)
        self.on_continue = on_continue
        self.on_quit = on_quit
        tk.Label(self, text=AB.PRODUCT_NAME, bg=T.BG, fg=T.ACCENT, font=(T.FONT_TITLE, 16, "bold"),
                 anchor="w").pack(side="top", fill="x")
        tk.Label(self, text="Please read before you go on.", bg=T.BG, fg=T.MUTED, font=T.font(9), anchor="w",
                 justify="left").pack(side="top", fill="x", pady=(px(2), px(8)))
        foot = tk.Frame(self, bg=T.BG)
        foot.pack(side="bottom", fill="x", pady=(px(10), 0))
        self.continue_btn = RoundButton(foot, CONTINUE, self._continue, kind="danger", height=36, size=10)
        self.continue_btn.pack(side="right")
        self.quit_btn = RoundButton(foot, QUIT, self._quit, kind="secondary", height=36, size=10)
        self.quit_btn.pack(side="right", padx=(0, px(8)))
        card = RoundFrame(self, fill=T.ERROR_BG, outline=T.ERROR, pad=12, outline_width=2)
        card.pack(side="top", fill="both", expand=True)
        self.card = card
        self.text = tk.Text(card.inner, bg=T.ERROR_BG, fg=T.TEXT, font=T.font(11), wrap="word", relief="flat", bd=0,
                            highlightthickness=0, padx=px(6), pady=px(4), cursor="arrow", width=1, height=1,
                            selectbackground=T.ACCENT_LO, selectforeground=T.ON_ACCENT, insertwidth=0, takefocus=0)
        bar = ttk.Scrollbar(card.inner, orient="vertical", style="Dark.Vertical.TScrollbar", command=self.text.yview)
        self.text.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y", padx=(px(6), 0))
        self.text.pack(side="left", fill="both", expand=True)
        self._fill()
        self.text.bind("<MouseWheel>", lambda e: (self.text.yview_scroll(int(-e.delta / 120) or (-1 if e.delta > 0 else 1), "units"), "break")[1])

    def _fill(self):
        t = self.text
        t.tag_configure("title", font=(T.FONT_TITLE, 17, "bold"), foreground=T.ERROR, spacing3=px(12))
        t.tag_configure("body", font=T.font(11, "semibold"), foreground=T.TEXT, spacing3=px(12))
        t.tag_configure("disclaimer", font=T.font(8), foreground=T.MUTED, spacing3=px(8))
        t.tag_configure("see", font=T.font(9), foreground=T.TEXT)
        for tag, line in (("title", TITLE), ("body", BODY), ("disclaimer", DISCLAIMER), ("see", SEE_LICENCE)):
            t.insert("end", line + "\n", tag)
        t.configure(state="disabled")

    def _continue(self):
        self.on_continue()

    def _quit(self):
        self.on_quit()
