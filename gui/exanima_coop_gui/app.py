""









import datetime
import os
import queue
import sys
import threading
import time
import traceback
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk

from . import about as AB
from . import blocked as BL
from . import bugreport as BR
from . import compact as C
from . import directview as DV
from . import downgrade as DG
from . import handoff as HO
from . import licence as LIC
from . import notice as NT
from . import risk as RK
from . import lifecycle as L
from . import passwords as PW
from . import picks as P
from . import settings as S
from . import steamjoin as SJ
from . import steamview as SV
from . import theme as T
from . import updatecheck as UC
from . import whatsnew as WN
from .api import LauncherApi
from .theme import px
from .widgets import (Banner, BodyRow, body_title, CheckBox, DISCORD_HI, DISCORD_MUTED, CopyIcon, Dot, EyeToggle, Field, FolderIcon, footer_row_h, hide_all_tips, IconLink, InfoTip,
                      FolderPanel, FolderTabs, ProgressBar, RoundButton, RoundFrame, ScrollArea, Segmented, Spinner, Tooltip)

try:


    from . import devflags as DEV
except ImportError:
    DEV = None

W, H = 460, 690










LEFT_W = C.LEFT_W
PANEL_W = C.PANEL_W
COL_GAP = C.COL_GAP
W_WIDE, H_WIDE = C.WIDE_W, C.WIDE_H


GAP, CARD_PAD, SEG_H, BUTTON_H = C.GAP, C.CARD_PAD, C.SEG_H, C.BUTTON_H


def wide_fits(work, scale):
    ""

    left, _top, right, _bottom = work
    return int(round(W_WIDE * scale)) <= (right - left) - int(round(16 * scale)) - 2 * int(round(8 * scale))


ROSTER_POLL_MS = 1500


ROSTER_REFRESH_MS = 2000

UPDATE_FETCH = UC.fetch

WN_CHROME = 150


CLOSE_WAIT_S = 4.0

MAX_LAN_ROWS = 3

FLASH_MS = 1400

MOD_DIR_NONE = "Not installed yet"


UNINSTALL_TITLE = "Remove the co-op mod"
UNINSTALL_NOTHING = "Nothing of the mod is in this folder."
UNINSTALL_FALLBACK = "No usable install record was found: only files identical to this download's copies are removed."
UNINSTALL_DONE = "The co-op mod was removed from the game folder."
UNINSTALL_PARTIAL = "Not everything was removed. What happened:"


def uninstall_view(plan):
    ""



    if not plan.get("ok"):
        return {"error": plan.get("error") or "The game folder cannot be checked.", "dir": None, "delete": [], "keep": [], "missing": [], "dirs": [], "note": None, "go": None}
    delete = [e.get("path", "") for e in plan.get("delete") or []]
    keep = ["%s (%s)" % (e.get("path", ""), e.get("why", "")) for e in plan.get("keep") or []]
    n = len(delete)
    return {
        "error": None,
        "dir": plan.get("game_dir"),
        "delete": delete,
        "missing": list(plan.get("missing") or []),
        "keep": keep,
        "dirs": list(plan.get("dirs") or []) if n else [],
        "note": UNINSTALL_FALLBACK if plan.get("fallback") else None,
        "go": ("Uninstall %d file%s" % (n, "" if n == 1 else "s")) if n else None,
    }




LAUNCH_CHECKING = "The game folder is still being checked. Wait a moment, then start again."
LAUNCH_NO_GAME = "Exanima %s was not found, so UEMM cannot start it."
LAUNCH_FALLBACK = {
    "not_installed": "UEMM is not installed in this game folder. Click Install at the top, then start again.",
    "update_available": "This game folder has another UEMM version than this launcher. Click Update at the top, then start again.",
}
LAUNCH_NOT_READY = "The game folder is not ready for UEMM."


def launch_refusal(gate, install, allow_inject=False):
    ""





    if not gate:
        return LAUNCH_CHECKING
    if not gate.get("ok"):
        return LAUNCH_NO_GAME % (gate.get("expected") or "")
    if not install:
        return LAUNCH_CHECKING
    if not install.get("ok"):
        return install.get("error") or LAUNCH_NOT_READY
    launch = install.get("launch")
    if isinstance(launch, dict):
        if launch.get("ok"):
            return None
        if allow_inject and launch.get("kind") == "not_installed":
            return None
        return launch.get("text") or LAUNCH_NOT_READY
    st = install.get("status")
    if st == "installed" or (allow_inject and st == "not_installed"):
        return None
    return LAUNCH_FALLBACK.get(st) or install.get("detail") or LAUNCH_NOT_READY


def install_row(install):
    ""


    r = install or {}
    st = r.get("status") if r.get("ok") else "error"
    if st == "update_available" and (r.get("launch") or {}).get("kind") == "newer":
        row = ("A newer mod version is installed", "accent", ("Install", "primary"))
    else:
        row = {

            "installed": ("Mod installed in this game folder", "ok", ("Uninstall", "ghost")),
            "not_installed": ("Mod not installed in this game folder", "accent", ("Install", "primary")),
            "update_available": ("Mod update available", "accent", ("Update", "primary")),

            "foreign": ("Another mod's winmm.dll is in the game folder", "error", (C.FOREIGN_BUTTON, "ghost")),
        }.get(st, (r.get("error", "Cannot check the game folder"), "error", None))
    if st in ("not_installed", "update_available") and not r.get("has_payload"):
        row = ("The mod's game files are missing from this download", "error", None)
    return row


def install_tip(install):
    ""

    r = install or {}
    if r.get("ok") and r.get("status") == "foreign":
        return C.FOREIGN_TIP
    return (r.get("launch") or {}).get("text") or r.get("detail")




NEW_CHARACTER = {"char_id": 0, "id_hex": "", "name": "New character", "background": "", "free": True, "held_by": None,
                 "state": "make your character in the game with CREATE", "new": True}



JOIN_NOTE_DIRECT = C.JOIN_NOTE_DIRECT
JOIN_NOTE_STEAM = C.JOIN_NOTE_STEAM


class Options:
    ""

    def __init__(self, argv):
        self.debug_tools = bool(DEV and DEV.debug_tools(argv))
        self.allow_inject = "--inject" in argv
        self.game_dir = None
        self.log_level = None

        self.join_lobby = SJ.parse_join_lobby(argv)

        self.after_game = SJ.parse_after_game(argv) if self.join_lobby is not None else None

        self.licence_bypass = bool(DEV and DEV.licence_bypass(argv))
        self.show_licence = bool(DEV and DEV.show_licence(argv))
        for i, a in enumerate(argv):
            if a == "--game-dir" and i + 1 < len(argv):
                self.game_dir = argv[i + 1]
            if a == "--log-level" and i + 1 < len(argv):
                self.log_level = argv[i + 1]


def log_level_for(cli_level, detailed):
    ""


    if cli_level:
        return cli_level
    return "debug" if detailed else None


def elide(path, n=54):
    return path if len(path) <= n else path[: n // 3] + "…" + path[-(n - n // 3 - 1):]


def fmt_mb(b):
    return "%.1f MB" % (b / 1048576.0)


def log_error(text):
    try:
        d = os.path.dirname(S.settings_path())
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "gui-error.log"), "a", encoding="utf-8") as f:
            f.write("%s\n%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), text))
    except OSError:
        pass


class App:
    def __init__(self, root, opts):
        self.root = root
        self.opts = opts
        self.s = S.load()
        self.q = queue.Queue()
        self.api = None
        self.api_error = None
        self.api_block = None
        try:
            self.api = LauncherApi()
        except OSError as e:
            self.api_error = str(e)
            self.api_block = BL.classify(e, "library")



        self.steam_ui = False



        self.manual = True
        self.manual_note = None

        self.mod_version = None


        self.info = None
        if self.api is not None:
            try:
                info = self.api.api_info()
                self.info = info if isinstance(info, dict) else None
                self.steam_ui = SV.steam_ui_on(info)
                self.manual = SV.manual_on(info)
                self.mod_version = info.get("mod_version") if isinstance(info, dict) else None
            except Exception:
                self.steam_ui = False
        _, self.manual_note = SV.manual_tab(self.manual)
        self.identity = AB.identity_line(self.info, DEV.package_note(os.path.dirname(os.path.abspath(__file__))) if DEV else None)


        if self.api is not None and self.opts.after_game:
            try:
                self.api.process_alive(self.opts.after_game)
            except Exception:
                pass


        self.pending_invite = None
        self.inbox = HO.inbox_dir(os.path.dirname(S.settings_path()))
        self.host_steam = False
        self.host_access = "friends"
        self.host_code = None
        self.host_portmap = False
        self.portmap_live = False
        self.portmap_stopper = None
        self.portmap_starter = None
        self._closing = False
        self.gate = None
        self.install = None
        self.install_checking = True
        self.host_info = None
        self.roster = None
        self.roster_addr = None
        self.selected = None
        self.game = None
        self.downloading = False
        self.view = None

        self.dg = None
        self.dg_phase = None
        self.dg_token = 0
        self.dg_free = None
        self.dg_old = []
        self.dg_busy = False



        self.waiting = False
        self.wait_token = 0
        self.repick = None


        self.list_token = 0
        self.hid_for_game = False


        self.route = None
        self.steam_enabled = False
        self.steam_note = None
        self.router = None
        self.router_busy = False
        self.router_asked = False


        self.pub_lookup = None

        root.title(AB.window_title(self.info))
        root.configure(bg=T.BG)


        root.resizable(True, True)
        self._user_size = None
        T.init_scale(root)
        T.setup_ttk(root)

        self.wide = wide_fits(T.work_area(), T._scale)
        self.win_w, self.win_h = (W_WIDE, H_WIDE) if self.wide else (W, H)
        root.geometry("%dx%d" % (px(self.win_w), px(self.win_h)))
        root.minsize(px(min(self.win_w, W)), px(360))
        root.bind("<Configure>", self._on_root_configure, add="+")


        self._away = False
        root.bind("<FocusOut>", self._on_focus_out, add="+")
        root.bind("<FocusIn>", self._on_focus_in, add="+")


        self._icons = self._load_app_icons()
        try:
            self._icon = self._icons[0] if self._icons else T.make_icon(64)
            root.iconphoto(True, *(self._icons or [self._icon]))
        except tk.TclError:
            pass
        root.report_callback_exception = self._on_tk_error






        self.gui_slot = S.claim_gui_slot()
        self.v_name = tk.StringVar(value=S.slot_name(self.s, self.gui_slot))

        self.connecting = False
        self.v_host_pw = tk.StringVar(value=self.s["host_password"])
        self.v_join_pw = tk.StringVar(value=self.s["join_password"])
        self.v_addr = tk.StringVar(value=self.s["last_ip"])
        self.v_console = tk.BooleanVar(value=self.s["show_console"])
        self.v_remember = tk.BooleanVar(value=self.s["remember_password"])
        self.v_close = tk.BooleanVar(value=self.s["close_on_start"])
        self.v_detailed = tk.BooleanVar(value=self.s["detailed_logs"])

        self.v_update_check = tk.BooleanVar(value=self.s["update_check"])
        self.update_latest = None


        self.v_tile = tk.BooleanVar(value=self.s["demo_tile"] and C.advanced_shown(self.opts.debug_tools))


        self.v_open_port = tk.BooleanVar(value=self.s["open_port"])

        self.access = SV.access_value(self.s.get("steam_access"))



        self.v_code = tk.StringVar(value="")
        self.v_host_direct = tk.BooleanVar(value=False)
        self.v_join_direct = tk.BooleanVar(value=False)
        self.players = self.s["players"]
        self.mode = self.s["mode"]


        self.route = self.s["route"]






        self.risk_gate = None
        self.licence_gate = None
        self.notice_gate = None
        self.licence_text = LIC.load_text()
        if RK.needs_warning(self.s, bypass=opts.licence_bypass, force=opts.show_licence):
            self._show_risk_gate()
            return
        self._after_risk()

    def _after_risk(self):
        ""
        if LIC.needs_agreement(self.s, self.licence_text, bypass=self.opts.licence_bypass, force=self.opts.show_licence):
            self._show_licence_gate()
            return
        self._after_licence()

    def _show_risk_gate(self):
        ""
        self.root.protocol("WM_DELETE_WINDOW", self._licence_quit)
        self.risk_gate = RK.RiskGate(self.root, self._risk_continue, self._licence_quit)
        self.risk_gate.pack(fill="both", expand=True, padx=(px(C.PAD_L), px(C.PAD_L)), pady=(px(12), px(14)))
        self._fit_gate()

    def _risk_continue(self):
        ""
        self.s[RK.SETTINGS_KEY] = RK.__version__
        disk = S.load()
        disk[RK.SETTINGS_KEY] = RK.__version__
        S.save(disk)
        self.risk_gate.destroy()
        self.risk_gate = None
        self._after_risk()

    def _after_licence(self):
        ""
        if NT.needs_notice(self.s, bypass=self.opts.licence_bypass, force=self.opts.show_licence):
            self._show_notice_gate()
            return
        self._build_main()

    def _fit_gate(self):
        root = self.root
        T.dark_title_bar(root)
        x, y, w, h, _ = T.fit_window(px(self.win_h), px(self.win_w), T.work_area(), T._scale, None)
        root.geometry("%dx%d+%d+%d" % (w, h, x, y))

    def _show_notice_gate(self):
        ""
        self.root.protocol("WM_DELETE_WINDOW", self._licence_quit)
        self.notice_gate = NT.NoticeGate(self.root, self._notice_ok, self._licence_quit)
        self.notice_gate.pack(fill="both", expand=True, padx=(px(C.PAD_L), px(C.PAD_L)), pady=(px(12), px(14)))
        self._fit_gate()

    def _notice_ok(self):
        ""
        self.s[NT.SETTINGS_KEY] = NT.__version__
        disk = S.load()
        disk[NT.SETTINGS_KEY] = NT.__version__
        S.save(disk)
        self.notice_gate.destroy()
        self.notice_gate = None
        self._build_main()

    def _show_licence_gate(self):
        ""
        root = self.root
        root.protocol("WM_DELETE_WINDOW", self._licence_quit)
        self.licence_gate = LIC.LicenceGate(root, self.licence_text, self._licence_agreed, self._licence_quit)
        self.licence_gate.pack(fill="both", expand=True, padx=(px(C.PAD_L), px(C.PAD_L)), pady=(px(12), px(14)))
        T.dark_title_bar(root)
        x, y, w, h, _ = T.fit_window(px(self.win_h), px(self.win_w), T.work_area(), T._scale, None)
        root.geometry("%dx%d+%d+%d" % (w, h, x, y))

    def _licence_agreed(self):
        ""

        rec = LIC.record(self.licence_text)
        self.s[LIC.SETTINGS_KEY] = rec
        disk = S.load()
        disk[LIC.SETTINGS_KEY] = rec
        S.save(disk)
        self.licence_gate.destroy()
        self.licence_gate = None
        self._after_licence()

    def _licence_quit(self):
        ""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def _build_main(self):
        ""
        root = self.root
        root.protocol("WM_DELETE_WINDOW", self._ask_close)
        root.bind("<Return>", self._on_return)



        self.outer = tk.Frame(root, bg=T.BG)
        self.outer.pack(fill="both", expand=True, padx=(px(C.PAD_L), px(C.PAD_R)), pady=(px(12), px(12)))
        self._build_header()
        self._build_footer()
        self.banner = Banner(self.outer, wrap=self.win_w - 70)
        self.scroll = ScrollArea(self.outer, gutter=C.GUTTER, on_change=lambda: self._fit_soon())
        self.scroll.pack(side="top", fill="both", expand=True)
        self.content = self.scroll.body
        self._build_gate_card()







        self.cols = tk.Frame(self.content, bg=T.BG)
        self.cols.pack(side="top", fill="both", expand=True, pady=(px(GAP + 2), 0))
        self.cols.grid_columnconfigure(0, weight=1)
        self.cols.grid_rowconfigure(0, weight=1)
        self.left = tk.Frame(self.cols, bg=T.BG)
        self.left.grid(row=0, column=0, sticky="nsew")


        self.route_top = tk.Frame(self.left, bg=T.BG)
        tab_row = tk.Frame(self.route_top, bg=T.BG)
        tab_row.pack(side="top", fill="x")
        self.route_seg = FolderTabs(tab_row, [(SV.ROUTE_STEAM, "Steam"), (SV.ROUTE_MANUAL, "Manual")], SV.ROUTE_MANUAL,
                                    command=self._on_route_tab, height=SEG_H, tab_w=C.TOP_TAB_W)


        self.route_seg.disabled = {SV.ROUTE_STEAM}
        self.route_seg.on_disabled = self._on_route_greyed

        route_tip = lambda: self._route_tip(self._route_hovered())
        route_tip.at = lambda x, y: self._route_tip(self.route_seg.options[self.route_seg._index_at(x)][0])
        self.route_tip = Tooltip(self.route_seg, route_tip, at_cursor=True)
        self.route_seg.pack(side="left", anchor="sw")
        self.folder = FolderPanel(self.route_top, pad=C.FOLDER_PAD)
        self.folder.pack(side="top", fill="both", expand=True)
        self.route_seg.on_selected = self.folder.set_gap
        fi = self.folder.inner

        sub = tk.Frame(fi, bg=T.FOLDER)
        sub.pack(side="top", fill="x", pady=(0, px(GAP + 2)))
        self.sub_row = sub
        self.tabs = Segmented(sub, [("host", "Host"), ("join", "Join")], self.mode, command=self._on_mode, height=SEG_H)
        self.tabs.configure(width=px(C.SUB_TABS_W))
        self.tabs.pack(side="left")
        self.pn_title_text, self.pn_info_text = C.route_panel(True, True)
        self.pn_info = InfoTip(sub, lambda: "%s\n\n%s" % (self.pn_title_text, self.pn_info_text))
        self.pn_info.pack(side="left", padx=(px(8), 0))

        self.form_stage = tk.Frame(fi, bg=T.FOLDER)
        self.form_stage.pack(side="top", fill="both", expand=True)


        self.manual_off = tk.Frame(fi, bg=T.FOLDER)
        mo = tk.Frame(self.manual_off, bg=T.FOLDER)
        mo.pack(expand=True, pady=px(24))
        self.manual_off_title = tk.Label(mo, text=SV.MANUAL_DISABLED_TITLE, bg=T.FOLDER, fg=T.TEXT, font=T.font(20, "semibold"))
        self.manual_off_title.pack()
        self.manual_off_text = tk.Label(mo, text=SV.MANUAL_DISABLED_TEXT, bg=T.FOLDER, fg=T.MUTED, font=T.font(10),
                                        justify="center", wraplength=px(440 if self.wide else C.section_col_w(False, W) - 20))
        self.manual_off_text.pack(pady=(px(6), 0))
        self.stage = tk.Frame(self.left, bg=T.BG)
        self.stage.pack(side="top", fill="both", expand=True)
        self._placed = False
        self.views = {}
        self._build_host_view()
        self._build_join_view()
        self.v_name.trace_add("write", lambda *a: self._on_name())
        self._on_name(fit=False)
        self._build_roster_view()
        self._build_waiting_view()
        self._build_progress_view()
        self._build_running_view()
        self._build_gate_fail_view()
        self._build_advanced()

        T.dark_title_bar(root)
        self._fit_soon()
        root.after(40, self._drain)
        root.after(HO.POLL_MS, self._poll_inbox)
        if self.api is None:
            if self.api_block is not None and self.api_block["kind"] != "missing":

                self._gate_line(T.ERROR, self.api_block["title"], self.api_block["headline"])
            else:
                self._gate_line(T.ERROR, "The launcher library is missing", "coop_launcher.dll was not found. Your antivirus may have moved it to "
                                "quarantine. Extract the whole download again, keeping every file together.")
            self.set_actions(primary=("Close", root.destroy, True))
            self._show_checks(False)
            if self.api_block is not None:
                root.after(200, lambda: self._blocked_dialog(self.api_block))
        else:
            self._check_game()
            self._start_update_check()




    def _start_update_check(self):
        ""

        if not self.v_update_check.get() or not isinstance(self.mod_version, str):
            return
        ours = self.mod_version
        self.run_bg(lambda: UC.check(ours, True, fetch=UPDATE_FETCH), self._on_update)

    def _on_update(self, latest):
        ""
        if not isinstance(latest, dict) or not latest.get("version"):
            return
        self.update_latest = latest
        self.wn_new.configure(text=UC.banner(latest) + " ")
        self.wn_new.pack(side="left", before=self.wn_link)
        self.wn_sep.pack(side="left")
        self.wn_dl.pack(side="left")
        self._wn_item[1] = self._wn_width()
        self._flow_links()
        self._fit_soon()

    def _wn_width(self):
        ""
        f = tkfont.Font(root=self.root, font=T.font(8))
        text = WN.TITLE if self.update_latest is None else UC.banner(self.update_latest) + " " + WN.TITLE + " / " + WN.DOWNLOAD_LABEL
        return f.measure(text) + px(2)

    def _open_releases(self):
        self._open_url(UC.RELEASES_URL)

    def _whatsnew_dialog(self, latest=None):
        ""


        old = getattr(self, "wn_win", None)
        if old is not None and old.winfo_exists():
            old.destroy()
        win = tk.Toplevel(self.root)
        self.wn_win = win
        win.title(AB.PRODUCT_NAME + " - " + WN.TITLE)
        win.configure(bg=T.BG)
        win.transient(self.root)
        try:
            win.iconphoto(False, *(getattr(self, "_icons", None) or [self._icon]))
        except (AttributeError, tk.TclError):
            pass
        pad = tk.Frame(win, bg=T.BG)
        pad.pack(fill="both", expand=True, padx=px(16), pady=px(14))
        if latest:
            head = "UEMM %s" % latest["version"]
            sub = ("Released %s. " % latest["date"] if latest.get("date") else "") + "You have %s." % (self.mod_version or "an older version")
            md = latest.get("notes") or ""
        else:
            head, sub, md = None, None, WN.read_bundled()
        self.wn_source = "github" if latest else ("bundled" if md else "missing")
        blocks = WN.parse(md) if md else [("text", WN.MISSING)]
        if head:
            blocks = [("title", head), ("text", sub)] + blocks
        box = tk.Frame(pad, bg=T.SURFACE, highlightthickness=1, highlightbackground=T.BORDER)
        box.pack(fill="both", expand=True)

        work = T.work_area(T.window_handle(self.root))
        line = tkfont.Font(root=win, font=T.font(9)).metrics("linespace")
        self.wn_lines = C.whatsnew_lines(work[3] - work[1], line, px(WN_CHROME))
        txt = tk.Text(box, bg=T.SURFACE, fg=T.TEXT, font=T.font(9), wrap="word", relief="flat", bd=0, highlightthickness=0,
                      padx=px(12), pady=px(10), width=64, height=self.wn_lines, cursor="arrow", insertwidth=0)
        bar = ttk.Scrollbar(box, orient="vertical", style="Dark.Vertical.TScrollbar", command=txt.yview)
        txt.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)
        txt.tag_configure("title", font=T.font(13, "semibold"), spacing3=px(2))
        txt.tag_configure("heading", font=T.font(10, "semibold"), spacing1=px(10), spacing3=px(4))
        txt.tag_configure("text", foreground=T.MUTED, spacing1=px(2), spacing3=px(2))
        txt.tag_configure("bullet", lmargin1=px(4), lmargin2=px(16), spacing3=px(3))

        txt.tag_configure("caution_title", font=T.font(11, "bold"), foreground=T.ERROR, background=T.ERROR_BG,
                          spacing1=px(8), spacing3=px(4))
        txt.tag_configure("caution", foreground=T.ERROR, background=T.ERROR_BG, spacing3=px(6))
        for kind, text in blocks:
            txt.insert("end", ("•  " + text if kind == "bullet" else text) + "\n", (kind,))
        txt.configure(state="disabled")
        self.wn_text = txt
        self.wn_blocks = blocks
        row = tk.Frame(pad, bg=T.BG)
        row.pack(fill="x", pady=(px(12), 0))
        cb = CheckBox(row, WN.SETTING_LABEL, self.v_update_check, command=self._on_update_tick, size=9, info=WN.SETTING_TIP)
        cb.pack(side="left")
        self.wn_tick = cb

        def close():
            hide_all_tips()
            win.destroy()

        RoundButton(row, "Close", close, kind="secondary", height=34, size=10).pack(side="right")
        label, tip = (WN.DOWNLOAD_LABEL, WN.DOWNLOAD_TIP) if latest else (WN.CHECK_LABEL, WN.CHECK_TIP)
        self.wn_go = RoundButton(row, label, self._open_releases, kind="primary", height=34, size=10)
        self.wn_go.pack(side="right", padx=(0, px(10)))
        Tooltip(self.wn_go, tip)
        win.protocol("WM_DELETE_WINDOW", close)
        win.bind("<Escape>", lambda e: close())
        T.dark_title_bar(win)
        return win

    def _on_update_tick(self):
        ""
        on = bool(self.v_update_check.get())
        self.s["update_check"] = on
        disk = S.load()
        disk["update_check"] = on
        S.save(disk)




    def run_bg(self, fn, done):
        def work():
            try:
                r = fn()
            except Exception as e:
                log_error(traceback.format_exc())
                r = {"ok": False, "kind": "internal", "error": "Unexpected error: %s" % e}
            self.q.put((done, r))

        threading.Thread(target=work, daemon=True).start()

    def _drain(self):
        try:
            while True:
                cb, r = self.q.get_nowait()
                cb(r)
        except queue.Empty:
            pass

        self.root.after(250 if self._hidden() else 40, self._drain)

    def _hidden(self):
        ""
        try:
            return self.root.state() == "iconic"
        except tk.TclError:
            return False

    def _on_tk_error(self, exc, val, tb):
        log_error("".join(traceback.format_exception(exc, val, tb)))
        self.show_error("Something went wrong: %s (details in %%APPDATA%%\\ExanimaCoop\\gui-error.log)" % val)

    def show_error(self, text):
        self.banner.show(text, "error")
        self._pack_banner(True)

    def show_failure(self, err, context, text):
        ""


        view = BL.classify(err, context)
        if view is None:
            self.show_error(text)
            return None
        log_error("Windows block (%s, error %s): %s" % (view["kind"], view["code"], BL.error_text(err)))
        self.show_error(view["banner"])
        self._blocked_dialog(view)
        return view

    def _blocked_dialog(self, view):
        ""


        old = getattr(self, "block_win", None)
        if old is not None and old.winfo_exists():
            old.destroy()
        win = tk.Toplevel(self.root)
        self.block_win = win
        self.block_text = BL.dialog_text(view)
        win.title(AB.PRODUCT_NAME + " - " + view["title"])
        win.configure(bg=T.BG)
        win.transient(self.root)
        try:
            win.iconphoto(False, *(getattr(self, "_icons", None) or [self._icon]))
        except (AttributeError, tk.TclError):
            pass
        wrap = 470
        pad = tk.Frame(win, bg=T.BG)
        pad.pack(fill="both", expand=True, padx=px(16), pady=px(14))
        self._label(pad, view["headline"], 13, T.TEXT, "semibold", wrap=wrap).pack(fill="x")
        self._label(pad, view["what"], 9, T.MUTED, wrap=wrap).pack(fill="x", pady=(px(4), px(10)))
        self._label(pad, "What you can do:", 9, T.MUTED, "semibold").pack(fill="x")
        for i, step in enumerate(view["steps"], 1):
            self._label(pad, "%d. %s" % (i, step), 9, T.TEXT, wrap=wrap).pack(fill="x", padx=(px(10), 0), pady=(px(3), 0))
        self._label(pad, view["more_help"], 9, T.MUTED, wrap=wrap).pack(fill="x", pady=(px(10), px(10)))
        row = tk.Frame(pad, bg=T.BG)
        row.pack(fill="x")

        def opener(url):
            def go():
                import webbrowser
                try:
                    webbrowser.open(url)
                except Exception:
                    pass
            return go

        RoundButton(row, "Close", win.destroy, kind="primary", height=36, size=10).pack(side="right")
        if C.DISCORD_URL:
            RoundButton(row, "Open the Discord", opener(C.DISCORD_URL), kind="secondary", height=36, size=10).pack(side="right", padx=(0, px(10)))
        if view.get("faq_url"):
            RoundButton(row, "Open the FAQ", opener(view["faq_url"]), kind="secondary", height=36, size=10).pack(side="right", padx=(0, px(10)))

    def show_info(self, text, kind="info"):
        self.banner.show(text, kind)
        self._pack_banner(True)

    def clear_banner(self):
        self.banner.hide()
        self._pack_banner(False)

    def _pack_banner(self, on):
        if on:
            if not self.banner.winfo_manager():

                self.banner.pack(side="bottom", fill="x", padx=(0, px(12)), pady=(px(10), 0), before=self.scroll)
        else:
            self.banner.pack_forget()
        self._fit_soon()

    def _fit_soon(self):
        self.root.after_idle(self._fit)

    def _fit(self):
        ""



        self.root.update_idletasks()
        self.scroll._sync()
        self.root.update_idletasks()
        req = self.root.winfo_reqheight()
        if self.view in ("host", "join"):



            banner = (self.banner.winfo_reqheight() + px(10)) if self.banner.winfo_manager() else 0
            self._form_h = max(getattr(self, "_form_h", 0), req - banner)
            req = max(req, self._form_h)
        natural = max(px(self.win_h), req)
        mapped = self.root.winfo_ismapped()
        hwnd = T.window_handle(self.root) if self._placed and mapped else None
        pos = None
        if self._placed:

            pos = (self.root.winfo_x(), self.root.winfo_y()) if mapped else self.geometry[:2]
        x, y, w, h, _ = T.fit_window(natural, px(self.win_w), T.work_area(hwnd), T._scale, pos)
        if self._user_size is not None:

            w, h = self._user_size
        if not self._placed or abs(self.root.winfo_height() - h) > 1 or (x, y) != pos or not mapped:
            self.root.geometry("%dx%d+%d+%d" % (w, h, x, y))
        self.geometry = (x, y, w, h)
        self._placed = True

    @staticmethod
    def _load_app_icons():
        ""

        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        out = []
        for n in (256, 128, 64, 48, 32, 24, 16):
            p = os.path.join(base, "app-icon-%d.png" % n)
            if os.path.isfile(p):
                try:
                    out.append(tk.PhotoImage(file=p))
                except tk.TclError:
                    pass
        return out

    def _on_root_configure(self, e):
        ""

        if e.widget is not self.root or not getattr(self, "_placed", False):
            return
        g = getattr(self, "geometry", None)
        if not g:
            return
        if abs(e.width - g[2]) > 2 or abs(e.height - g[3]) > 2:
            self._user_size = (e.width, e.height)
            self.geometry = (g[0], g[1], e.width, e.height)

    def save_settings(self):
        s = self.s
        s["mode"] = self.mode
        s["route"] = self.route if self.route in (SV.ROUTE_STEAM, SV.ROUTE_MANUAL) else SV.ROUTE_STEAM

        S.merge_other_names(s, S.load(), self.gui_slot)
        s[S.name_key(self.gui_slot)] = self.v_name.get().strip()

        s["last_ip"] = self.v_addr.get().strip()
        s["players"] = self.players
        s["show_console"] = bool(self.v_console.get())
        s["remember_password"] = bool(self.v_remember.get())
        s["close_on_start"] = bool(self.v_close.get())
        s["detailed_logs"] = bool(self.v_detailed.get())
        s["update_check"] = bool(self.v_update_check.get())
        s["demo_tile"] = bool(self.v_tile.get())
        s["open_port"] = bool(self.v_open_port.get())
        s["steam_access"] = SV.access_value(self.access)
        s["host_password"] = self.v_host_pw.get() if s["remember_password"] else ""
        s["join_password"] = self.v_join_pw.get() if s["remember_password"] else ""
        S.save(s)

    def _ask_close(self):
        ""

        note = None
        if self.portmap_live and self.api is not None:
            try:
                note = DV.close_note(self.api.portmap_status(), int((self.host_info or {}).get("port") or 27500))
            except Exception:
                note = None
        if note and not messagebox.askokcancel(DV.CLOSE_TITLE, note, parent=self.root):
            return
        self._on_close()

    def _on_close(self):
        if self._closing:
            return
        self._closing = True
        if (self.downloading or self.waiting) and self.api:
            self.api.cancel()
        try:
            self.save_settings()
        finally:



            waiter = self._stop_portmap_async(1500)
            if waiter is None:
                self.root.destroy()
            else:
                try:
                    self.root.withdraw()
                except tk.TclError:
                    pass
                self._destroy_when_done(waiter, time.time() + CLOSE_WAIT_S)

    def _destroy_when_done(self, waiter, deadline):
        if waiter.is_alive() and time.time() < deadline:
            self.root.after(50, self._destroy_when_done, waiter, deadline)
            return
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def _stop_portmap_async(self, wait_ms):
        ""


        live, self.portmap_live = self.portmap_live and self.api is not None, False
        stopper, self.portmap_stopper = self.portmap_stopper, None
        if not live and stopper is None:
            return None
        api, starter = self.api, self.portmap_starter

        def work():
            if live:
                _end_portmap(api, starter, wait_ms)
            if stopper is not None:
                stopper.join(wait_ms / 1000.0)

        t = threading.Thread(target=work, daemon=True)
        t.start()
        return t

    def _start_portmap(self, port):
        ""


        self.portmap_live = True
        api = self.api

        def work():
            try:
                api.portmap_start(port)
            except Exception:
                pass

        self.portmap_starter = threading.Thread(target=work, daemon=True)
        self.portmap_starter.start()

    def _stop_portmap_soon(self):
        ""
        if not self.portmap_live or self.api is None:
            return
        self.portmap_live = False
        api, starter = self.api, self.portmap_starter
        self.portmap_stopper = threading.Thread(target=lambda: _end_portmap(api, starter, 3000), daemon=True)
        self.portmap_stopper.start()

    def _on_return(self, e):
        if isinstance(e.widget, ttk.Combobox):
            return
        self.primary.invoke()




    def _build_header(self):

        h = tk.Frame(self.outer, bg=T.BG)
        h.pack(side="top", fill="x", padx=(0, px(12)), pady=(0, px(GAP)))

        top = tk.Frame(h, bg=T.BG)
        top.pack(fill="x")
        self._build_header_icons(top)
        row = tk.Frame(top, bg=T.BG)
        row.pack(side="left", anchor="w")


        big, small = (T.FONT_TITLE, 18, "bold"), (T.FONT_TITLE, 11, "bold")
        try:
            lift = max(0, tkfont.Font(root=self.root, font=big).metrics("descent") - tkfont.Font(root=self.root, font=small).metrics("descent"))
        except tk.TclError:
            lift = px(3)
        styles = {"small": (small, T.MUTED), "title": (big, T.TEXT), "accent": (big, T.ACCENT)}
        for text, role in AB.HEADER_PARTS:
            font, fg = styles[role]
            lab = tk.Label(row, text=text, bg=T.BG, fg=fg, font=font, padx=0)
            if role == "small":
                lab.pack(side="left", anchor="s", pady=(0, lift))
            else:
                lab.pack(side="left", anchor="s")

        ident = getattr(self, "identity", None) or AB.identity_line(None)
        self.identity_label = tk.Label(h, text=ident, bg=T.BG, fg=T.DIM, font=T.font(8), anchor="w", padx=0)
        self.identity_label.pack(side="bottom", anchor="w")
        sub = AB.SUBTITLE
        if self.opts.debug_tools and DEV:
            sub = (sub + DEV.SUBTITLE_NOTE) if sub else DEV.SUBTITLE_NOTE.strip(" ·")
        if not sub:
            return
        sl = tk.Label(row if self.wide else h, text=sub, bg=T.BG, fg=T.DIM if not self.opts.debug_tools else T.ACCENT, font=T.font(9))
        if self.wide:
            sl.pack(side="left", anchor="s", padx=(px(12), 0), pady=(0, px(4)))
        else:
            sl.pack(anchor="w")

    def _build_header_icons(self, top):
        ""




        icons = tk.Frame(top, bg=T.BG)
        icons.pack(side="right", anchor="center", padx=(px(14), 0))


        discord_px = px(20)
        row_h = footer_row_h(discord_px)

        def icon(glyph, command, tip, colors=None):
            kw = {"colors": colors} if colors else {}
            w = IconLink(icons, glyph, command, tip, size=20, row_h=row_h, **kw)
            w.pack(side="left", anchor="s", padx=(0, px(6)))
            return w


        self.report_link = icon("bug", self._report_clicked, C.REPORT_ICON_TIP)
        if C.DISCORD_URL:
            self.discord_link = icon("discord", lambda: self._open_url(C.DISCORD_URL), C.DISCORD_TIP, colors=(DISCORD_MUTED, DISCORD_HI))
        if C.GITHUB_URL:
            self.github_link = icon("github", lambda: self._open_url(C.GITHUB_URL), C.GITHUB_TIP)

    def _open_url(self, url):
        ""

        import webbrowser
        try:
            webbrowser.open(url)
        except Exception:
            pass

    def _build_gate_card(self):
        ""

        card = RoundFrame(self.content, pad=10)
        card.pack(side="top", fill="x")
        self.gate_card = card
        i = card.inner
        self.gate_left = tk.Frame(i, bg=T.SURFACE)
        self.gate_left.pack(side="left" if self.wide else "top", fill="x", expand=True, anchor="n")
        r1 = tk.Frame(self.gate_left, bg=T.SURFACE)
        r1.pack(fill="x")
        self.gate_icon_holder = tk.Frame(r1, bg=T.SURFACE, width=px(16), height=px(16))
        self.gate_icon_holder.pack(side="left", padx=(px(2), px(10)))
        self.gate_icon_holder.pack_propagate(False)
        self.gate_spinner = Spinner(self.gate_icon_holder, size=16)
        self.gate_dot = Dot(self.gate_icon_holder, T.OK, size=10)
        gate_wrap = C.GATE_WRAP if self.wide else W - 110
        self.gate_title = tk.Label(r1, text="", bg=T.SURFACE, fg=T.TEXT, font=T.font(10, "semibold"), anchor="w", justify="left", wraplength=px(gate_wrap))
        self.gate_title.pack(side="left", fill="x", expand=True)
        sub_row = tk.Frame(self.gate_left, bg=T.SURFACE)
        sub_row.pack(fill="x", padx=(px(28), 0), pady=(px(1), 0))
        self.gate_sub = tk.Label(sub_row, text="", bg=T.SURFACE, fg=T.DIM, font=T.font(8), anchor="w", justify="left", wraplength=px(gate_wrap))

        self.gate_sub_room = px(gate_wrap) - px(14) - px(4)
        self.gate_sub.pack(side="left")
        Tooltip(self.gate_sub, lambda: (self.gate or {}).get("dir"))

        self.gate_open = FolderIcon(sub_row, lambda: self._open_folder((self.gate or {}).get("dir")), size=14)
        Tooltip(self.gate_open, lambda: "Open this folder" if self.gate_open.enabled else "This folder no longer exists")

        self.inst_row = tk.Frame(i, bg=T.SURFACE)
        if self.wide:
            tk.Frame(self.inst_row, bg=T.BORDER, width=1).pack(side="left", fill="y", padx=(px(10), px(10)))
        else:
            tk.Frame(self.inst_row, bg=T.BORDER, height=1).pack(fill="x", pady=(px(8), px(7)))
        r2 = tk.Frame(self.inst_row, bg=T.SURFACE)
        r2.pack(side="left" if self.wide else "top", fill="x", expand=True)
        inst_col = tk.Frame(r2, bg=T.SURFACE)
        inst_col.pack(side="left", fill="x", expand=True)
        inst_line = tk.Frame(inst_col, bg=T.SURFACE)
        inst_line.pack(fill="x")
        self.inst_dot = Dot(inst_line, T.DIM, size=10)
        self.inst_dot.pack(side="left", padx=(px(3), px(10)))
        inst_wrap = C.INST_WRAP if self.wide else W - 224
        self.inst_label = tk.Label(inst_line, text="Checking the game folder…", bg=T.SURFACE, fg=T.MUTED, font=T.font(9), anchor="w", justify="left",
                                   wraplength=px(inst_wrap))
        self.inst_label.pack(side="left", fill="x", expand=True)
        self.inst_btn = RoundButton(r2, "Install", self._install_clicked, kind="primary", height=28, size=9)

        Tooltip(self.inst_btn, lambda: C.install_button_tip(self.inst_btn.text))
        Tooltip(self.inst_label, lambda: install_tip(self.install))


        inst_sub_row = tk.Frame(inst_col, bg=T.SURFACE)
        inst_sub_row.pack(fill="x", padx=(px(3) + px(10) + px(10), 0), pady=(px(1), 0))
        self.inst_sub = tk.Label(inst_sub_row, text="", bg=T.SURFACE, fg=T.DIM, font=T.font(8), anchor="w", justify="left")
        self.inst_sub_room = px(inst_wrap) - px(14) - px(4)
        self.inst_sub.pack(side="left")
        Tooltip(self.inst_sub, lambda: self._mod_dir())
        self.inst_open = FolderIcon(inst_sub_row, lambda: self._open_folder(self._mod_dir()), size=14)
        self.inst_open.pack(side="left", anchor="n", padx=(px(4), 0))
        Tooltip(self.inst_open, lambda: "Open this folder" if self.inst_open.enabled else
                ("This folder no longer exists" if self._mod_dir() else "The mod is not installed yet"))
        self._mod_dir_line()

    def _pack_inst_row(self):
        if self.wide:
            self.inst_row.pack(side="right", fill="y")
        else:
            self.inst_row.pack(side="top", fill="x")

    def _gate_line(self, color, title, sub="", spinning=False):
        self.gate_spinner.pack_forget()
        self.gate_dot.pack_forget()
        if spinning:
            self.gate_spinner.pack(expand=True)
            self.gate_spinner.start()
        else:
            self.gate_spinner.stop()
            self.gate_dot.set(color)
            self.gate_dot.pack(expand=True)
        self.gate_title.configure(text=title, fg=T.TEXT if color != T.ERROR else T.ERROR)
        self.gate_sub.configure(text=sub)
        self.gate_open.pack_forget()

    def _one_line_dir(self, path, suffix="", label=None, room=None):
        ""

        label, room = label or self.gate_sub, self.gate_sub_room if room is None else room
        try:
            f = tkfont.Font(root=self.root, font=label.cget("font"))
            fits = lambda t: f.measure(t + suffix) <= room
        except tk.TclError:
            fits = lambda t: len(t + suffix) <= 40
        return C.elide_path(path, fits)

    def _check_game(self):
        self.clear_banner()
        self._gate_line(T.ACCENT, "Checking your Exanima install…", "Looking in every Steam library", spinning=True)
        self.inst_row.pack_forget()
        self._form_chrome(False)
        self._show_advanced(False)
        self._show_view(None)
        self.set_actions(primary=("Please wait", None, False))
        self.run_bg(lambda: self.api.game_check(self.opts.game_dir), self._on_gate)

    def _on_gate(self, r):
        self.gate = r
        if r.get("ok"):
            src = {"steam_depot": "  (Steam console download)", "explicit": "  (folder given on the command line)"}.get(r.get("source"), "")
            self._gate_line(T.OK, "Exanima %s found and verified" % r.get("version", ""), self._one_line_dir(r.get("dir", ""), src) + src)
            if r.get("dir"):
                self.gate_open.set(enabled=DG.folder_target(r["dir"]) is not None)
                self.gate_open.pack(side="left", anchor="n", padx=(px(4), 0))
            self._pack_inst_row()
            self._refresh_install()

            self.steam_enabled, label, self.steam_note = SV.route_tabs(self.steam_ui, r, self.manual)


            greyed = () if self.steam_enabled else (SV.ROUTE_STEAM,)
            self.route_seg.set_options([(SV.ROUTE_STEAM, label), (SV.ROUTE_MANUAL, "Manual")], disabled=greyed)
            self._set_route(SV.initial_route(self.steam_enabled, self.route, self.manual), sync=False)
            self._form_chrome(True)




            lobby, after = self.opts.join_lobby, self.opts.after_game
            if self.pending_invite:
                (lobby, after), self.pending_invite = self.pending_invite, None
            self.opts.join_lobby = None
            if not self._apply_invite(lobby, after):
                self._show_mode()
            if self.host_info is None:
                self.run_bg(self.api.host_info, self._on_host_info)
        else:
            self._gate_line(T.ERROR, "Exanima %s not found" % r.get("expected", ""), DG.gate_sub(r.get("installed")))
            self.inst_row.pack_forget()
            self._show_advanced(False)
            self._fill_gate_fail(r)
            self._show_view("gate_fail")
            self._dg_start()
            self._show_checks(False)

    def _mod_dir(self):
        ""

        r = self.install or {}
        if not self.install_checking and r.get("ok") and r.get("status") in ("installed", "update_available"):
            return r.get("game_dir") or None
        return None

    def _mod_dir_line(self):
        ""

        d = self._mod_dir()

        foreign = self._install_foreign()
        if foreign:
            self.inst_open.pack_forget()
        elif not self.inst_open.winfo_manager():
            self.inst_open.pack(side="left", anchor="n", padx=(px(4), 0))
        if d:
            self.inst_sub.configure(text=self._one_line_dir(d, label=self.inst_sub, room=self.inst_sub_room))
            self.inst_open.set(enabled=DG.folder_target(d) is not None)
        else:
            self.inst_sub.configure(text=C.FOREIGN_SUB if foreign else ("" if self.install_checking else MOD_DIR_NONE))
            self.inst_open.set(enabled=False)

    def _install_foreign(self):
        ""
        r = self.install or {}
        return not self.install_checking and bool(r.get("ok")) and r.get("status") == "foreign"

    def _has_focus(self):
        ""
        try:
            return bool(str(self.root.tk.call("focus")))
        except tk.TclError:
            return True

    def _on_focus_out(self, _e=None):

        self.root.after_idle(self._note_away)

    def _note_away(self):
        if not self._has_focus():
            self._away = True

    def _on_focus_in(self, _e=None):
        ""

        if not self._away:
            return
        self._away = False
        if self._install_foreign() and self.gate and self.gate.get("dir"):
            self._refresh_install()

    def _refresh_install(self, then=None):
        self.inst_btn.pack_forget()
        self.inst_dot.set(T.DIM)
        self.inst_label.configure(text="Checking the game folder…", fg=T.MUTED)
        self.install_checking = True
        self._mod_dir_line()

        def done(r):
            self._on_install_status(r)
            if then:
                then()

        self.run_bg(lambda: self.api.install_status(self.gate["dir"]), done)

    def _on_install_status(self, r):
        self.install, self.install_checking = r, False
        text, tone, btn = install_row(r)
        color = {"ok": T.OK, "accent": T.ACCENT}.get(tone, T.ERROR)
        self.inst_dot.set(color)
        self.inst_label.configure(text=text, fg=T.TEXT if color != T.ERROR else T.ERROR)
        self._mod_dir_line()
        self.inst_btn.pack_forget()
        if btn:
            self.inst_btn.configure_button(text=btn[0], kind=btn[1], enabled=True)
            self.inst_btn.pack(side="right", padx=(px(14), 0))
        self._update_start()

    def _install_clicked(self):
        st = (self.install or {}).get("status")
        d = self.gate["dir"]
        if st == "foreign":


            self._open_folder(d)
            return
        if st == "installed":

            self.inst_btn.configure_button(text="Checking…", enabled=False)

            def planned(plan):
                self.inst_btn.configure_button(text="Uninstall", enabled=True)
                self._uninstall_dialog(d, plan)

            self.run_bg(lambda: self.api.uninstall_plan(d), planned)
            return
        op, busy, ok_text = self.api.install, "Installing…", "Installed into %s. Steam's Play button still starts the normal game." % d
        self.inst_btn.configure_button(text=busy, enabled=False)

        def done(r):
            if r.get("ok"):
                self._on_install_status(r)
                self.show_info(ok_text, "ok")
            else:
                self._refresh_install()
                self.show_failure(r, "install", r.get("error", "The install failed."))

        self.run_bg(lambda: op(d), done)

    def _uninstall_dialog(self, d, plan):
        ""



        old = getattr(self, "uninst_win", None)
        if old is not None and old.winfo_exists():
            old.destroy()
        view = uninstall_view(plan)
        win = tk.Toplevel(self.root)
        self.uninst_win = win
        win.title(AB.PRODUCT_NAME + " - " + UNINSTALL_TITLE)
        win.configure(bg=T.BG)
        win.transient(self.root)
        try:
            win.iconphoto(False, *(getattr(self, "_icons", None) or [self._icon]))
        except (AttributeError, tk.TclError):
            pass
        wrap = 470
        pad = tk.Frame(win, bg=T.BG)
        pad.pack(fill="both", expand=True, padx=px(16), pady=px(14))
        self._label(pad, UNINSTALL_TITLE, 13, T.TEXT, "semibold").pack(fill="x")

        confirmed = view["dir"] or d
        self._label(pad, confirmed, 9, T.MUTED, wrap=wrap).pack(fill="x", pady=(px(2), px(10)))
        body = tk.Frame(pad, bg=T.BG)
        body.pack(fill="x")
        row = tk.Frame(pad, bg=T.BG)
        row.pack(fill="x", pady=(px(14), 0))
        ui = {"view": view, "delete": [], "dirs": [], "keep": [], "missing": [], "notes": [], "go": None, "cancel": None, "close": None, "body": body}
        self.uninst_ui = ui

        def heading(text):
            self._label(body, text, 9, T.MUTED, "semibold").pack(fill="x", pady=(px(6), px(2)))

        def line(text, fg, store):
            l = self._label(body, text, 9, fg, wrap=wrap)
            l.pack(fill="x", padx=(px(10), 0))
            store.append(l)

        if view["error"]:
            line(view["error"], T.ERROR, ui["notes"])
        elif not view["delete"]:
            line(UNINSTALL_NOTHING, T.TEXT, ui["notes"])
        else:
            heading("These files are removed:")
            for p in view["delete"]:
                line(p, T.TEXT, ui["delete"])
            if view["dirs"]:
                heading("Then these folders, only if nothing else is in them:")
                for p in view["dirs"]:
                    line(p, T.TEXT, ui["dirs"])
        if view["keep"]:
            heading("Left alone:")
            for k in view["keep"]:
                line(k, T.DIM, ui["keep"])
        if view["missing"] and view["go"]:
            heading("Not there (nothing to remove):")
            for k in view["missing"]:
                line(k, T.DIM, ui["missing"])
        if view["note"]:
            self._label(body, view["note"], 9, T.MUTED, wrap=wrap).pack(fill="x", pady=(px(8), 0))
        if view["go"]:
            self._label(body, "Only the files listed above are removed. Your saves and the game's own files stay where they are.", 9, T.MUTED, wrap=wrap).pack(fill="x", pady=(px(8), 0))

        def close():
            if win.winfo_exists():
                win.destroy()

        def finished(r):
            if not win.winfo_exists():
                return
            for w in body.winfo_children():
                w.destroy()
            ui["delete"], ui["dirs"], ui["keep"], ui["missing"], ui["notes"] = [], [], [], [], []

            result = r.get("result") or ("complete" if r.get("ok") else "refused")
            if result == "complete":
                heading(UNINSTALL_DONE)
            else:
                if result == "partial":
                    heading(UNINSTALL_PARTIAL)
                if r.get("error"):
                    line(r["error"], T.ERROR, ui["notes"])
            for n in r.get("notes") or []:
                line(n, T.TEXT if n.startswith("removed") else T.MUTED, ui["notes"])
            for b in (ui["go"], ui["cancel"]):
                if b is not None:
                    b.destroy()
            ui["go"] = ui["cancel"] = None
            ui["close"] = RoundButton(row, "Close", close, kind="primary", height=36, size=10)
            ui["close"].pack(side="right")
            if r.get("status"):
                self._on_install_status(r)
            else:
                self._refresh_install()

        def go():
            ui["go"].configure_button(text="Removing…", enabled=False)
            ui["cancel"].configure_button(enabled=False)
            self.run_bg(lambda: self.api.uninstall(confirmed), finished)

        if view["go"]:
            ui["go"] = RoundButton(row, view["go"], go, kind="primary", height=36, size=10)
            ui["go"].pack(side="right")
            ui["cancel"] = RoundButton(row, "Cancel", close, kind="secondary", height=36, size=10)
            ui["cancel"].pack(side="right", padx=(0, px(10)))
        else:
            ui["close"] = RoundButton(row, "Close", close, kind="secondary", height=36, size=10)
            ui["close"].pack(side="right")
        T.dark_title_bar(win)

    def _launch_refusal(self):
        ""
        return launch_refusal(self.gate, None if self.install_checking else self.install, self.opts.allow_inject)

    def _ensure_installed(self, cont):
        ""



        why = self._launch_refusal()
        if why is None:
            cont()
            return
        self.show_error(why)
        self._back_to_form()




    def _build_footer(self):
        f = tk.Frame(self.outer, bg=T.BG)
        f.pack(side="bottom", fill="x", padx=(0, px(12)), pady=(px(GAP + 2), 0))
        self.footer = f





        self.log_checks = tk.Frame(f, bg=T.BG)
        self.checks = tk.Frame(f, bg=T.BG)



        self.cb_remember = None
        if C.remember_tick_shown(self.manual):
            self.cb_remember = CheckBox(self.checks, "Remember password", self.v_remember, size=9, info=C.REMEMBER_TIP)
            self.cb_remember.pack(anchor="w")


        self.cb_close = CheckBox(self.checks, "Close the launcher when the game starts", self.v_close, size=9,
                                 info=lambda: SV.close_on_start_tip(self.steam_ui, self.manual))
        self.cb_close.pack(anchor="w", pady=(px(4) if self.cb_remember is not None else 0, 0))
        grid = C.footer_checks(self.wide) == "grid"
        self.cb_console = CheckBox(self.log_checks, "Show console window", self.v_console, size=9, info=C.CONSOLE_TIP)
        self.cb_console.pack(side="top" if grid else "left", anchor="w")


        self.cb_detailed = CheckBox(self.log_checks, "Detailed logs (for bug reports)", self.v_detailed, size=9, info=C.DETAILED_TIP)
        if grid:
            self.cb_detailed.pack(side="top", anchor="w", pady=(px(4), 0))
        else:
            self.cb_detailed.pack(side="left", anchor="w", padx=(px(16), 0))
        self.primary = RoundButton(f, "Start", None, kind="primary", width=140, height=BUTTON_H, size=11)
        self.primary.pack(side="right", anchor="e")
        self.secondary = RoundButton(f, "Back", None, kind="secondary", height=BUTTON_H, size=10)
        self._show_checks(True)

    def _show_checks(self, on):
        if on:


            if C.footer_checks(self.wide) == "grid":

                col = C.footer_checks_anchor(self.cb_remember is not None, True)
                if not self.checks.winfo_manager():
                    self.checks.pack(side="left", anchor=col, before=self.primary)


                if not self.log_checks.winfo_manager():
                    if self.secondary.winfo_manager():
                        self._log_stepped_aside = True
                    else:
                        self.log_checks.pack(side="left", anchor=col, padx=(px(24), 0), after=self.checks)
            else:
                if not self.log_checks.winfo_manager():
                    self.log_checks.pack(side="bottom", fill="x", pady=(px(4), 0), before=self.primary)
                if not self.checks.winfo_manager():
                    self.checks.pack(side="left", anchor="w", before=self.primary)
        else:
            self._log_stepped_aside = False
            self.checks.pack_forget()
            self.log_checks.pack_forget()

    def set_actions(self, primary, secondary=None):
        text, cmd, enabled = primary
        self.primary.configure_button(text=text, command=cmd or (lambda: None), enabled=enabled)
        if secondary:
            self.secondary.configure_button(text=secondary[0], command=secondary[1] or (lambda: None), enabled=secondary[2] if len(secondary) > 2 else True)
            if not self.secondary.winfo_manager():

                self.secondary.pack(side="right", padx=(0, px(10)))
            if C.footer_checks(self.wide) == "grid" and self.log_checks.winfo_manager():
                self.log_checks.pack_forget()
                self._log_stepped_aside = True
        else:
            self.secondary.pack_forget()
            if getattr(self, "_log_stepped_aside", False):
                self._log_stepped_aside = False
                if self.checks.winfo_manager() and not self.log_checks.winfo_manager():
                    self.log_checks.pack(side="left", anchor="w", padx=(px(24), 0), after=self.checks)




    def _show_view(self, name):
        hide_all_tips()
        if name and name not in ("host", "join") and self.route_top.winfo_manager():
            self._form_chrome(False)
        for n, v in self.views.items():
            if n != name:
                v.pack_forget()
        if name in ("host", "join"):

            self.views[name].pack(fill="both", expand=True, anchor="n")
        elif name:
            self.views[name].pack(fill="x", anchor="n")
        self.view = name
        self._fit_soon()

    def _label(self, parent, text, size=9, fg=T.MUTED, weight="normal", wrap=None, **kw):
        l = tk.Label(parent, text=text, bg=parent.cget("bg"), fg=fg, font=T.font(size, weight), anchor="w", justify="left", **kw)
        if wrap:
            l.configure(wraplength=px(wrap))
        return l

    def _address_rows(self, parent):
        ""



        box = tk.Frame(parent, bg=parent.cget("bg"))
        dim = T.dim_for(box.cget("bg"))

        def make_row(title):
            r = tk.Frame(box, bg=box.cget("bg"))
            r.pack(fill="x", pady=(0, px(3)))
            self._label(r, title, 9, T.MUTED, "semibold", width=9).pack(side="left")


            val = tk.Label(r, text="fetching…", bg=box.cget("bg"), fg=dim, font=(T.FONT_MONO, 10), anchor="w", width=1)
            val.pack(side="left", fill="x", expand=True)

            btn = CopyIcon(r)
            Tooltip(btn, "Copy")
            return val, btn

        public = make_row("Public IP")

        v6 = make_row("IPv6")
        Tooltip(v6[0], C.IPV6_TIP)
        v6[0].master.pack_forget()
        lan = []
        more = {"text": None, "last": 0}

        def add_lan_row():
            k = len(lan)
            lan.append(make_row("LAN IP" if k == 0 else ""))
            Tooltip(lan[k][0], lambda: more["text"] if k == more["last"] else None)

        add_lan_row()
        box.copy_rows = {"public": public, "lan": lan, "ipv6": v6}


        shown = {"public": False}
        eye = EyeToggle(public[0].master, lambda on: (shown.__setitem__("public", on), refresh()))
        Tooltip(eye, "Show / hide your public IP")


        ask_info = InfoTip(public[0].master, DV.PUBLIC_LOOKUP_TIP, size=13)
        ask_btn = RoundButton(public[0].master, DV.PUBLIC_LOOKUP_LABEL, self._public_ip_clicked, kind="ghost", height=26, size=9)
        box.lookup_parts = (ask_btn, ask_info)

        def show_public(port):
            val, btn = public
            state, ip = DV.public_row(self.router, self.router_busy, self.pub_lookup, bool(getattr(self.api, "has_public_lookup", False)))
            if ip:
                ask_btn.pack_forget()
                ask_info.pack_forget()
                show("public", public, ip, port)
                return
            val.configure(text=DV.PUBLIC_ROW_TEXT.get(state, ""), fg=dim)
            btn.pack_forget()
            eye.pack_forget()
            if state in ("ask", "failed"):

                ask_info.pack(side="right", padx=(px(5), 0))
                ask_btn.pack(side="right", after=ask_info)
            else:
                ask_btn.pack_forget()
                ask_info.pack_forget()

        def show(key, row, ip, port):
            val, btn = row
            if self.host_info is None and key != "public":
                val.configure(text="fetching…", fg=dim)
                btn.pack_forget()
            elif ip:
                text = "%s:%s" % (ip, port)

                hidden = key in ("public", "ipv6") and not shown["public"]
                masked = "[••••:••••:…]:%s" % port if key == "ipv6" else "•••.•••.•••.•••:%s" % port
                val.configure(text=masked if hidden else text, fg=dim if hidden else T.TEXT)
                btn.configure_button(text="Copy", command=lambda t=text, b=btn: self._copy(t, b))
                btn.pack(side="right")
                if key == "public":
                    eye.pack(side="right", padx=(0, px(6)), after=btn)
            else:
                val.configure(text="not available", fg=dim)
                btn.pack_forget()
                if key == "public":
                    eye.pack_forget()

        def refresh():
            info = self.host_info or {}
            port = info.get("port", 27500)
            lans = list(info.get("lan_ips") or [])
            show_public(port)

            v6_ip = DV.ipv6_address(info)
            if v6_ip:
                v6[0].master.pack(fill="x", pady=(0, px(3)), after=public[0].master)
                show("ipv6", v6, v6_ip, port)
            else:
                v6[0].master.pack_forget()

            n = max(1, min(len(lans), MAX_LAN_ROWS))
            while len(lan) < n:
                add_lan_row()
            for k, row in enumerate(lan):
                row[0].master.pack_forget()
                if k < n:
                    row[0].master.pack(fill="x", pady=(0, px(3)))
                    show("lan", row, lans[k] if k < len(lans) else None, port)
            extra = lans[n:]
            more["last"] = n - 1
            more["text"] = ("Other addresses of this PC: " + ", ".join("%s:%s" % (ip, port) for ip in extra)) if extra else None

        return box, refresh

    def _password_row(self, parent):
        ""



        box = tk.Frame(parent, bg=parent.cget("bg"))
        r = tk.Frame(box, bg=box.cget("bg"))
        r.pack(fill="x", pady=(0, px(4)))
        self._label(r, "Password", 9, T.MUTED, "semibold", width=9).pack(side="left")
        val = tk.Label(r, text="", bg=box.cget("bg"), fg=T.TEXT, font=(T.FONT_MONO, 10), anchor="w")
        val.pack(side="left", fill="x", expand=True)
        btn = RoundButton(r, "Copy", None, kind="ghost", height=26, size=9)
        btn.pack(side="right")
        eye = EyeToggle(r, lambda on: draw())
        eye.pack(side="right", padx=(0, px(6)))
        Tooltip(eye, "Show / hide the lobby password")

        def draw():
            pw = self.v_host_pw.get()
            val.configure(text=pw if eye.shown else "•" * min(len(pw), 14), fg=T.TEXT if eye.shown else T.DIM)
            btn.configure_button(text="Copy", command=lambda t=pw: self._copy(t, btn))

        def refresh(show):
            eye.shown = bool(show)
            eye._draw()
            draw()

        return box, refresh

    def _copy(self, text, btn=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        if btn:
            self._flash(btn, "Copied", "Copy")

    def _flash(self, btn, text, back):
        ""
        btn.configure_button(text=text)
        self.root.after(FLASH_MS, lambda: btn.winfo_exists() and btn.configure_button(text=back))

    def _copy_field(self, var, btn):
        ""
        text = var.get()
        if text.strip():
            self._copy(text, btn)

    def _paste(self, var, btn, field=None, pick=None):
        ""



        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            text = ""
        picked = pick(text) if pick is not None else None
        text = text.strip()
        text = picked or (text.splitlines()[0].strip()[:200] if text else "")
        if not text:
            self._flash(btn, "Empty", "Paste")
            return
        var.set(text)
        if field is not None:
            field.entry.icursor("end")




    def _section(self, name):
        ""




        sec = tk.Frame(self.form_stage, bg=T.FOLDER)
        self.views[name] = sec
        a = tk.Frame(sec, bg=T.FOLDER)
        b = tk.Frame(sec, bg=T.FOLDER)
        if C.route_placement(self.wide) == "beside":
            sec.grid_columnconfigure(0, weight=1, uniform="section")
            sec.grid_columnconfigure(1, weight=1, uniform="section")
            a.grid(row=0, column=0, sticky="nwe")
            b.grid(row=0, column=1, sticky="nwe", padx=(px(C.SECTION_GAP), 0))
        else:
            sec.grid_columnconfigure(0, weight=1)
            a.grid(row=0, column=0, sticky="nwe")
            b.grid(row=1, column=0, sticky="nwe", pady=(px(GAP + 2), 0))
        return a, b

    def _build_manual_host_part(self, parent):
        ""


        wrap = C.panel_wrap(self.wide, W)
        self.pn_wrap = wrap
        bg = parent.cget("bg")
        mh = tk.Frame(parent, bg=bg)
        self.pn_manual_host = mh

        box, self._refresh_host_addr = self._address_rows(mh)
        box.pack(fill="x")
        self.host_addr_box = box
        tk.Frame(mh, bg=T.FOLDER_EDGE, height=1).pack(fill="x", pady=(px(4), px(7)))



        row = tk.Frame(mh, bg=bg)
        row.pack(fill="x")
        self.router_row = row
        self.router_dot = Dot(row, T.DIM, size=10)
        self.router_dot.pack(side="left", anchor="n", padx=(px(2), px(8)), pady=(px(4), 0))
        self.router_label = self._label(row, DV.ROUTER_CHECKING, 9, T.MUTED, wrap=wrap - 50)
        self.router_label.pack(side="left", anchor="n")
        self.router_info_text = C.ROUTER_HOW
        self.router_info = InfoTip(row, lambda: self.router_info_text)
        self.router_info.pack(side="left", anchor="n", padx=(px(5), 0), pady=(px(1), 0))
        self.router_again = tk.Label(mh, text="Check again", bg=bg, fg=T.dim_for(bg), font=T.font(8), cursor="hand2", anchor="w")
        self.router_again.bind("<Button-1>", lambda e: self._router_check())

        self.cb_open_port = CheckBox(mh, DV.OPEN_PORT_LABEL, self.v_open_port, size=9, info=DV.OPEN_PORT_TIP)
        self.cb_open_port.label.configure(wraplength=px(wrap - 50), justify="left", anchor="w")
        self.cb_open_port.pack(anchor="w", pady=(px(7), 0))

        fw = tk.Frame(mh, bg=bg)
        fw.pack(fill="x", pady=(px(5), 0))
        self.pn_steps = self._label(fw, DV.MANUAL_HINT, 8, T.dim_for(bg))
        self.pn_steps.pack(side="left")
        self.pn_steps_text = C.forward_info()
        self.pn_steps_info = InfoTip(fw, lambda: self.pn_steps_text, size=13)
        self.pn_steps_info.pack(side="left", padx=(px(5), 0))

    def _form_chrome(self, on):
        ""


        hide_all_tips()
        if on:
            self.stage.pack_forget()
            if not self.route_top.winfo_manager():
                self.route_top.pack(side="top", fill="both", expand=True)
            self.left.grid_configure(sticky="nsew", padx=(0, 0))
        else:
            self.route_top.pack_forget()
            if not self.stage.winfo_manager():
                self.stage.pack(side="top", fill="both", expand=True)

            side = max(0, (C.content_width(self.win_w, T._scale) - px(W - 40)) // 2) if self.wide else 0
            self.left.grid_configure(sticky="nsew", padx=(side, side))
        self._fit_soon()

    def _lock_tabs(self, locked):
        ""
        self.tabs.set_enabled(not locked)
        self.route_seg.set_enabled(not locked)

    def _set_route(self, route, sync=True):
        ""

        self.route = route
        self.route_seg.set(route)
        direct = SV.route_direct(route)
        self.v_host_direct.set(direct)
        self.v_join_direct.set(direct)
        if sync:
            self._sync_route_ui()
            self._fit_soon()
        else:
            self._sync_password_fields()

    def _sync_password_fields(self):
        ""



        shown = SV.password_shown(self.steam_ui, self.route) and not SV.manual_off_shown(self.manual, self.route)
        host_pw = getattr(self, "f_host_pw", None)
        if host_pw is not None:
            if shown and not host_pw.winfo_manager():
                host_pw.pack(fill="x", pady=(px(GAP), 0), before=self.host_players_row)
            elif not shown and host_pw.winfo_manager():
                host_pw.pack_forget()
                self.host_pw_note.pack_forget()
            self._on_host_pw()
        join_pw = getattr(self, "f_join_pw", None)
        if join_pw is not None:
            if shown and not join_pw.winfo_manager():
                join_pw.pack(fill="x", pady=(px(GAP), 0))
            elif not shown and join_pw.winfo_manager():
                join_pw.pack_forget()

    def _on_route_tab(self, route):
        self.clear_banner()
        self._set_route(route)
        if self.mode == "host":
            self._refresh_host_addr()
        self._update_start()

    def _on_route_greyed(self, v):
        ""
        self.show_info(SV.greyed_note(v, self.steam_note, self.manual_note) or SV.STEAM_OFF)

    def _route_tip(self, value):
        ""


        if value != SV.ROUTE_STEAM:
            return None
        return SV.greyed_note(value, self.steam_note, self.manual_note)

    def _route_hovered(self):
        ""
        i = getattr(self.route_seg, "_hover", None)
        try:
            return self.route_seg.options[i][0] if i is not None else None
        except (IndexError, TypeError):
            return None

    def _sync_route_panel(self):
        ""



        hide_all_tips()

        manual = self.manual and ((not self.steam_ui) or SV.route_direct(self.route))
        host = self.mode == "host"
        self.pn_title_text, self.pn_info_text = C.route_panel(manual, host)
        if host:
            want = self.pn_manual_host if manual else self.host_steam_box
        else:
            want = self.f_addr if manual else self.f_code
        for part in (self.pn_manual_host, self.host_steam_box, self.f_addr, self.f_code):
            if part is not None and part is not want and part.winfo_manager():
                part.pack_forget()
        if want is not None and not want.winfo_manager():
            want.pack(fill="x")
        if manual and host:
            if not self.router_asked:
                self._router_check()
            else:
                self._refresh_router()

    def _router_check(self):
        ""
        if self.router_busy or not self.manual:
            return
        self.router_asked = True
        if self.api is None or not getattr(self.api, "has_router_check", False):
            self.router = {"ok": False}
            self._refresh_router()
            return
        self.router_busy = True
        self.router = None
        self._refresh_router()

        def done(r):
            self.router_busy = False
            self.router = r if isinstance(r, dict) else {"ok": False}
            self._refresh_router()

        self.run_bg(self.api.router_check, done)

    def _public_ip_clicked(self):
        ""


        if self.api is None or self.pub_lookup == DV.LOOKUP_BUSY or not self.manual:
            return
        self.pub_lookup = DV.LOOKUP_BUSY
        self._refresh_addresses()

        def done(r):
            self.pub_lookup = r if isinstance(r, dict) else {"ok": False}

            if self.router_asked:
                self._refresh_router()
            else:
                self._refresh_addresses()

        self.run_bg(self.api.public_ip_lookup, done)

    def _refresh_addresses(self):
        ""
        for refresh in (getattr(self, "_refresh_host_addr", None), getattr(self, "_refresh_run_addr", None)):
            if refresh:
                refresh()

    def _ensure_router_check(self):
        ""

        if not self.router_asked and self.manual:
            self._router_check()

    def _refresh_router(self):
        ""

        self._refresh_addresses()
        pub = DV.looked_up_ip(self.pub_lookup)
        kind, text = DV.router_note(None if self.router_busy else self.router, pub, self.steam_enabled)
        self.router_dot.set({"ok": T.OK, "cgnat": T.ACCENT, "double": T.ACCENT}.get(kind, T.DIM))
        line, self.router_info_text = C.router_line(kind, text)
        self.router_label.configure(text=line, fg=T.TEXT if kind in ("cgnat", "double") else T.MUTED)
        self.pn_steps_text = C.forward_info((self.router or {}).get("gateway"))
        again = kind != "checking" and getattr(self.api, "has_router_check", False)
        if again and not self.router_again.winfo_manager():
            self.router_again.pack(anchor="w", padx=(px(20), 0), pady=(px(1), 0), after=self.router_row)
        elif not again:
            self.router_again.pack_forget()
        self._fit_soon()

    def _build_host_view(self):


        i, way = self._section("host")
        self.f_name_host = Field(i, "Your name", self.v_name, "Your name", info=C.NAME_HOST_TIP)
        self.f_name_host.pack(fill="x")

        self.name_note_host = self._label(i, "", 8, T.ERROR, wrap=C.form_wrap(self.wide, W))



        self.f_host_pw = Field(i, "Lobby password", self.v_host_pw, "Type one or press Generate", secret=True, info=C.HOST_PW_TIP)
        self.f_host_pw.pack(fill="x", pady=(px(GAP), 0))
        self.b_gen_pw = self.f_host_pw.add_button("Generate", self._generate_host_pw,
                                                  "Makes a random password that is easy to read out, and shows it so you can give it to your friends.")
        self.b_copy_pw = self.f_host_pw.add_button("Copy", lambda: self._copy_field(self.v_host_pw, self.b_copy_pw), "Copies the password, to paste it to your friends.")

        self.host_pw_note = self._label(i, C.HOST_PW_NEEDED, 8, T.ACCENT, wrap=C.form_wrap(self.wide, W))
        self.v_host_pw.trace_add("write", lambda *a: self._on_host_pw())


        fr = tk.Frame(i, bg=T.FOLDER)
        fr.pack(fill="x", pady=(px(GAP + 2), px(3)))
        self.host_players_row = fr
        self._label(fr, "Max players", 9, T.MUTED, "semibold").pack(side="left")
        self.players_info = InfoTip(fr, C.PLAYERS_TIP)
        self.players_info.pack(side="left", padx=(px(5), 0))
        self.bg_note = self._label(fr, "", 8, T.FOLDER_DIM)
        self.bg_note.pack(side="right")
        self.seg_players = Segmented(i, [(n, str(n)) for n in (1, 2, 3, 4)], self.players, command=self._on_players, height=SEG_H - 2)
        self.seg_players.pack(fill="x")

        self._build_manual_host_part(way)


        self.host_steam_box = None
        if self.steam_ui:
            sb = tk.Frame(way, bg=T.FOLDER)
            self.host_steam_box = sb


            fa = tk.Frame(sb, bg=T.FOLDER)
            fa.pack(fill="x", pady=(0, px(3)))
            self._label(fa, "Who can join", 9, T.MUTED, "semibold").pack(side="left")
            self.access_info = InfoTip(fa, lambda: C.access_info(self.access))
            self.access_info.pack(side="left", padx=(px(5), 0))
            self.seg_access = Segmented(sb, list(SV.ACCESS_CHOICES), self.access, command=self._on_access, height=SEG_H - 2)
            self.seg_access.pack(fill="x")

            cr = tk.Frame(sb, bg=T.FOLDER)
            cr.pack(fill="x", pady=(px(GAP + 2), 0))
            self._label(cr, "Join code", 9, T.MUTED, "semibold", width=9).pack(side="left")
            self._label(cr, C.STEAM_CODE_LATER, 9, T.FOLDER_DIM).pack(side="left")
        self._on_players(self.players, save=False)
        self._on_host_pw()

    def _host_pw_ok(self):
        ""

        if not SV.host_password_needed(self.steam_ui, SV.route_direct(self.route)):
            return True
        return bool(self.v_host_pw.get().strip())

    def _on_host_pw(self):
        ""
        empty = not self._host_pw_ok()
        if empty and not self.host_pw_note.winfo_manager() and self.f_host_pw.winfo_manager():
            self.host_pw_note.pack(fill="x", pady=(px(4), 0), after=self.f_host_pw)
            self._fit_soon()
        elif not empty and self.host_pw_note.winfo_manager():
            self.host_pw_note.pack_forget()
            self._fit_soon()
        self._update_start()

    def _generate_host_pw(self):
        ""


        self.v_host_pw.set(PW.random_password())
        self.f_host_pw.reveal(True)

    def _update_start(self):
        ""

        if self.connecting:
            return

        can = SV.connect_possible(self.steam_ui, self.steam_enabled, self.manual, self.route)

        ready = self._launch_refusal() is None
        if self.view == "host":
            self.set_actions(primary=("Start hosting", self._start_host, can and ready and self._host_pw_ok() and self._name_ok()))
        elif self.view == "join":
            self.set_actions(primary=("Connect", self._connect, can and ready and self._name_ok()))

    def _name_ok(self):
        ""
        return S.launcher_name_problem(self.v_name.get()) is None

    def _on_name(self, fit=True):
        ""

        problem = S.launcher_name_problem(self.v_name.get())

        typed = bool(S.clean_name(self.v_name.get()))
        for field, note in ((self.f_name_host, self.name_note_host), (self.f_name_join, self.name_note_join)):
            field.set_error(problem is not None and typed)
            note.configure(text=problem or "")
            if problem and not note.winfo_manager():
                note.pack(fill="x", pady=(px(4), 0), after=field)
            elif not problem and note.winfo_manager():
                note.pack_forget()
        self._update_start()
        if fit:
            self._fit_soon()

    def _on_access(self, v):
        ""
        self.access = SV.access_value(v)
        self.save_settings()
        self._fit_soon()

    def _on_players(self, n, save=True):
        ""
        self.players = n
        self.bg_note.configure(text=C.players_summary(n))
        self._update_start()
        self._fit_soon()

    def _build_join_view(self):

        i, way = self._section("join")
        self.f_name_join = Field(i, "Your name", self.v_name, "Your name", info=C.NAME_JOIN_TIP)
        self.f_name_join.pack(fill="x")

        self.name_note_join = self._label(i, "", 8, T.ERROR, wrap=C.form_wrap(self.wide, W))

        self.f_join_pw = Field(i, "Lobby password", self.v_join_pw, "From the host", secret=True)
        self.f_join_pw.pack(fill="x", pady=(px(GAP), 0))
        self.b_paste_pw = self.f_join_pw.add_button("Paste", lambda: self._paste(self.v_join_pw, self.b_paste_pw, self.f_join_pw),
                                                    "Pastes the password from the clipboard.")



        self.f_addr = Field(way, "Host address", self.v_addr, "e.g. 203.0.113.7  or  203.0.113.7:27500")
        self.b_paste_addr = self.f_addr.add_button("Paste", lambda: self._paste(self.v_addr, self.b_paste_addr, self.f_addr),
                                                   "Pastes the host's address from the clipboard.")
        self.f_code = None
        if self.steam_ui:
            self.f_code = Field(way, "Join code", self.v_code, "e.g. ABCD-1234", info=C.CODE_TIP)
            self.b_paste_code = self.f_code.add_button("Paste", lambda: self._paste(self.v_code, self.b_paste_code, self.f_code, SJ.find_join_code),
                                                       "Pastes the host's join code from the clipboard.")
            self.v_code.trace_add("write", lambda *a: self.f_code.set_error(False))

    def _build_roster_view(self):
        card = RoundFrame(self.stage, pad=14)
        self.views["roster"] = card
        i = card.inner
        self.ro_title = self._label(i, "Choose your character", 13, T.TEXT, "semibold", wrap=W - 80)
        self.ro_title.pack(fill="x")
        self.ro_sub = self._label(i, "", 9, T.MUTED, wrap=W - 80)
        self.ro_sub.pack(fill="x", pady=(px(2), px(10)))
        self.ro_list = tk.Frame(i, bg=T.SURFACE)
        self.ro_list.pack(fill="x")
        self.ro_note = self._label(i, "", 8, T.DIM, wrap=W - 80)
        self.ro_note.pack(fill="x", pady=(px(8), 0))

    def _build_waiting_view(self):
        ""
        card = RoundFrame(self.stage, pad=14)
        self.views["waiting"] = card
        i = card.inner
        top = tk.Frame(i, bg=T.SURFACE)
        top.pack(fill="x")
        icon = tk.Frame(top, bg=T.SURFACE, width=px(18), height=px(18))
        icon.pack(side="left", padx=(0, px(10)))
        icon.pack_propagate(False)
        self.wait_spin = Spinner(icon, size=18)
        self.wait_spin.pack(expand=True)
        self.wait_title = self._label(top, "Waiting for the host to enter the world…", 13, T.TEXT, "semibold", wrap=W - 110)
        self.wait_title.pack(side="left")
        self.wait_sub = self._label(i, "", 9, T.MUTED, wrap=W - 80)
        self.wait_sub.pack(fill="x", pady=(px(4), px(6)))
        self.wait_note = self._label(i, "You pick your character (or New character) once the host is in the game. This screen updates by itself.", 8, T.DIM, wrap=W - 80)
        self.wait_note.pack(fill="x")

    def _build_progress_view(self):
        card = RoundFrame(self.stage, pad=14)
        self.views["progress"] = card
        i = card.inner
        self.pr_title = self._label(i, "Downloading the host's save", 13, T.TEXT, "semibold", wrap=W - 80)
        self.pr_title.pack(fill="x")
        self.pr_sub = self._label(i, "", 9, T.MUTED, wrap=W - 80)
        self.pr_sub.pack(fill="x", pady=(px(2), px(16)))
        self.pr_bar = ProgressBar(i, height=10)
        self.pr_bar.pack(fill="x")
        row = tk.Frame(i, bg=T.SURFACE)
        row.pack(fill="x", pady=(px(8), 0))
        self.pr_bytes = self._label(row, "", 9, T.MUTED)
        self.pr_bytes.pack(side="left")
        self.pr_pct = self._label(row, "", 9, T.ACCENT, "semibold")
        self.pr_pct.pack(side="right")
        self.pr_status = self._label(i, "", 9, T.TEXT, wrap=W - 80)
        self.pr_status.pack(fill="x", pady=(px(14), 0))

    def _build_running_view(self):
        card = RoundFrame(self.stage, pad=14)
        self.views["running"] = card
        i = card.inner
        top = tk.Frame(i, bg=T.SURFACE)
        top.pack(fill="x")
        self.run_icon = tk.Frame(top, bg=T.SURFACE, width=px(18), height=px(18))
        self.run_icon.pack(side="left", padx=(0, px(10)))
        self.run_icon.pack_propagate(False)
        self.run_spin = Spinner(self.run_icon, size=18)
        self.run_dot = Dot(self.run_icon, T.OK, size=12)
        self.run_title = self._label(top, "Starting the game…", 13, T.TEXT, "semibold", wrap=W - 110)
        self.run_title.pack(side="left")
        self.run_sub = self._label(i, "", 9, T.MUTED, wrap=W - 80)
        self.run_sub.pack(fill="x", pady=(px(4), px(10)))
        self.run_addr_box, self._refresh_run_addr = self._address_rows(i)

        self.run_port_note = self._label(i, "", 8, T.DIM, wrap=W - 80)
        self.run_pw_box, self._refresh_run_pw = self._password_row(i)

        self.run_code_box = self.run_code_note = None
        if self.steam_ui:
            box = tk.Frame(i, bg=T.SURFACE)
            r = tk.Frame(box, bg=T.SURFACE)
            r.pack(fill="x", pady=(0, px(4)))
            self._label(r, "Join code", 9, T.MUTED, "semibold", width=9).pack(side="left")
            self.run_code_val = tk.Label(r, text="", bg=T.SURFACE, fg=T.DIM, font=(T.FONT_MONO, 10), anchor="w")
            self.run_code_val.pack(side="left", fill="x", expand=True)
            self.run_code_copy = RoundButton(r, "Copy", None, kind="ghost", height=26, size=9)
            Tooltip(self.run_code_copy, "Copies the join code, to paste it to your friends.")
            self.run_code_box = box
            self.run_code_note = self._label(i, "", 8, T.DIM, wrap=W - 80)
        self.run_log = tk.Label(i, text="", bg=T.SURFACE, fg=T.MUTED, font=(T.FONT_MONO, 8), anchor="w", justify="left", wraplength=px(W - 80))
        self.run_log.pack(fill="x")

    def _refresh_run_code(self):
        ""

        if self.run_code_box is None:
            return
        since = (self.game or {}).get("since") or time.time()
        view = SV.host_code_view(self.host_code, time.time() - since, self.host_access, self.manual)
        if view == getattr(self, "_run_code_shown", None) and self.run_code_val.cget("text"):
            return
        self._run_code_shown = view
        text, has, note, rows = view
        self.run_code_val.configure(text=text, fg=T.TEXT if has else T.DIM)
        if has:
            self.run_code_copy.configure_button(text="Copy", command=lambda t=text: self._copy(t, self.run_code_copy))
            if not self.run_code_copy.winfo_manager():
                self.run_code_copy.pack(side="right")
        else:
            self.run_code_copy.pack_forget()
        self.run_code_note.configure(text=note)
        if note and not self.run_code_note.winfo_manager():
            self.run_code_note.pack(fill="x", pady=(0, px(8)), after=self.run_code_box)
        elif not note:
            self.run_code_note.pack_forget()
        if rows and not self.run_addr_box.winfo_manager():
            self.run_addr_box.pack(fill="x", before=self.run_pw_box)
            self._refresh_run_addr()
            self._ensure_router_check()
        self._fit_soon()

    def _run_state(self, spinning, color=T.OK):
        self.run_spin.pack_forget()
        self.run_dot.pack_forget()
        if spinning:
            self.run_spin.pack(expand=True)
            self.run_spin.start()
        else:
            self.run_spin.stop()
            self.run_dot.set(color)
            self.run_dot.pack(expand=True)

    def _build_advanced(self):
        ""



        box = tk.Frame(self.content, bg=T.BG)
        self.adv_box = box
        self.adv_open = False
        links = tk.Frame(box, bg=T.BG)
        links.pack(fill="x")
        self.adv_links = links
        items = []
        icon_w = px(4) + px(13) + 2 * max(2, px(2))

        def item(text, size, icon):
            f = tk.Frame(links, bg=T.BG)


            items.append([f, tkfont.Font(root=links, font=T.font(size)).measure(text) + px(2) + (icon_w if icon else 0), True])
            return f



        adv_parent = item("▾  Advanced", 9, False) if C.advanced_shown(self.opts.debug_tools) else tk.Frame(box, bg=T.BG)
        self.adv_toggle = tk.Label(adv_parent, text="▸  Advanced", bg=T.BG, fg=T.DIM, font=T.font(9), cursor="hand2", anchor="w", bd=0, padx=0)
        self.adv_toggle.pack(side="left")
        self.adv_toggle.bind("<Button-1>", lambda e: self._toggle_advanced())





        wn = item(WN.TITLE, 8, False)
        self._wn_item = items[-1]
        self.wn_new = tk.Label(wn, text="", bg=T.BG, fg=T.ACCENT, font=T.font(8), bd=0, padx=0)
        self.wn_link = tk.Label(wn, text=WN.TITLE, bg=T.BG, fg=T.DIM, font=T.font(8), cursor="hand2", bd=0, padx=0)
        self.wn_link.pack(side="left")
        self.wn_sep = tk.Label(wn, text=" / ", bg=T.BG, fg=T.DIM, font=T.font(8), bd=0, padx=0)
        self.wn_dl = tk.Label(wn, text=WN.DOWNLOAD_LABEL, bg=T.BG, fg=T.DIM, font=T.font(8), cursor="hand2", bd=0, padx=0)
        for lab, cmd in ((self.wn_link, lambda: self._whatsnew_dialog(self.update_latest)), (self.wn_dl, self._open_releases)):
            lab.bind("<Button-1>", lambda e, c=cmd: c())
            lab.bind("<Enter>", lambda e, l=lab: l.configure(fg=T.ACCENT))
            lab.bind("<Leave>", lambda e, l=lab: l.configure(fg=T.DIM))
        Tooltip(self.wn_dl, WN.DOWNLOAD_TIP)
        about = AB.about_line(self.mod_version if isinstance(self.mod_version, str) else None)
        f = item(about, 8, True)
        self.about_label = self._label(f, about, 8, T.DIM, bd=0, padx=0)
        self.about_label.pack(side="left")
        self.about_info = InfoTip(f, AB.ABOUT_TIP, size=13)
        self.about_info.pack(side="left", padx=(px(4), 0))
        self._link_items = items
        self._link_rows = []
        self._flow_links()
        self.adv_body = tk.Frame(box, bg=T.BG)

        self.cb_tile = CheckBox(self.adv_body, "Demo layout: tile game windows", self.v_tile, size=9, info=C.TILE_INFO)
        self.cb_tile.pack(anchor="w", pady=(px(6), 0))

    def _flow_links(self):
        ""

        for f, _w, _s in self._link_items:
            f.pack_forget()
        for row in self._link_rows:
            row.destroy()
        self._link_rows = []
        shown = [it for it in self._link_items if it[2]]
        avail = C.content_width(self.win_w, T._scale) - px(8)
        gap = px(16)
        rows = C.flow_rows([it[1] for it in shown], avail, gap)
        for k, idx in enumerate(rows):
            row = tk.Frame(self.adv_links, bg=T.BG)
            row.pack(fill="x", pady=(px(3) if k else 0, 0))
            self._link_rows.append(row)
            for j in idx:
                f = shown[j][0]
                last = j == len(shown) - 1 and len(idx) > 1
                f.pack(in_=row, side="right" if last else "left", padx=(0 if (j == idx[0] or last) else gap, 0))
                f.lift(row)

    def _report_clicked(self):
        ""



        win = getattr(self, "report_win", None)
        if win is not None and win.winfo_exists():
            self.report_reload()
            win.deiconify()
            win.lift()
            return
        info = None
        if self.api is not None:
            try:
                info = self.api.api_info()
            except Exception:
                info = None

        def load():
            try:
                return BR.load(info)
            except Exception:
                log_error(traceback.format_exc())
                return BR.facts(None, info), BR.NO_SESSION

        facts, source = load()
        win = tk.Toplevel(self.root)
        self.report_win = win
        win.title(AB.PRODUCT_NAME + " - " + BR.TITLE)
        win.configure(bg=T.BG)
        win.transient(self.root)
        try:
            win.iconphoto(False, *(getattr(self, "_icons", None) or [self._icon]))
        except (AttributeError, tk.TclError):
            pass
        wrap = 470
        pad = tk.Frame(win, bg=T.BG)
        pad.pack(fill="both", expand=True, padx=px(16), pady=px(14))
        self._label(pad, BR.TITLE, 13, T.TEXT, "semibold").pack(fill="x")
        source_lbl = self._label(pad, source, 9, T.MUTED, wrap=wrap)
        source_lbl.pack(fill="x", pady=(px(2), px(4)))
        self._label(pad, BR.HINT, 9, T.TEXT, wrap=wrap).pack(fill="x", pady=(0, px(10)))
        head = tk.Frame(pad, bg=T.BG)
        head.pack(fill="x", pady=(0, px(3)))
        self._label(head, "This exact text is copied:", 9, T.MUTED, "semibold").pack(side="left", anchor="s")
        copy_btn = RoundButton(head, BR.COPY_LABEL, None, kind="ghost", height=26, size=9)
        copy_btn.pack(side="right")
        prev = tk.Text(pad, height=10, width=64, wrap="word", bg=T.SURFACE, fg=T.TEXT, relief="flat", font=(T.FONT_MONO, 9),
                       highlightthickness=1, highlightbackground=T.BORDER, padx=px(6), pady=px(4))
        prev.pack(fill="both", expand=True)
        self._label(pad, BR.DISCLAIMER, 8, T.DIM, wrap=wrap).pack(fill="x", pady=(px(8), 0))
        self._label(pad, BR.CHOICE, 9, T.MUTED, wrap=wrap).pack(fill="x", pady=(px(8), px(8)))
        row = tk.Frame(pad, bg=T.BG)
        row.pack(fill="x")
        note = self._label(pad, BR.PASTE_NOTE, 8, T.DIM, wrap=wrap)
        note.pack(fill="x", pady=(px(8), 0))
        state = {"text": "", "facts": facts}

        def refresh():
            if not win.winfo_exists():
                return
            state["text"] = BR.build_text(state["facts"])
            prev.configure(state="normal")
            prev.delete("1.0", "end")
            prev.insert("1.0", state["text"])
            prev.configure(state="disabled")

        def reload():
            state["facts"], line = load()
            source_lbl.configure(text=line)
            refresh()

        self.report_reload = reload

        def copy_report():
            refresh()
            self.root.clipboard_clear()
            self.root.clipboard_append(state["text"])

        def copy():
            copy_report()
            self._flash(copy_btn, "Copied", BR.COPY_LABEL)

        def door(label, after):

            def go():
                copy_report()
                url = dict(C.bugreport_targets(state["facts"])).get(label)
                if url:
                    self._open_url(url)
                note.configure(text=after, fg=T.TEXT, font=T.font(9))
            return go


        labels = [l for l, _u in C.bugreport_targets(facts)]
        if BR.GITHUB_LABEL in labels:
            RoundButton(row, BR.GITHUB_LABEL, door(BR.GITHUB_LABEL, BR.AFTER_GITHUB), kind="primary", height=36,
                        size=10).pack(side="right")
        if BR.DISCORD_LABEL in labels:
            RoundButton(row, BR.DISCORD_LABEL, door(BR.DISCORD_LABEL, BR.AFTER_DISCORD), kind="secondary", height=36,
                        size=10).pack(side="right", padx=(0, px(10)))
        RoundButton(row, "Close", win.destroy, kind="secondary", height=36, size=10).pack(side="right", padx=(0, px(10)))
        copy_btn.configure_button(command=copy)
        refresh()
        T.dark_title_bar(win)

    def _toggle_advanced(self, open_=None):
        self.adv_open = (not self.adv_open) if open_ is None else open_
        self._adv_title()
        if self.adv_open:
            self.adv_body.pack(fill="x")
        else:
            self.adv_body.pack_forget()
        self._fit_soon()

    def _adv_title(self):

        self.adv_toggle.configure(text=SV.advanced_label(self.adv_open, False))

    def _sync_route_ui(self):
        ""


        self._sync_route_panel()
        self._sync_password_fields()
        self._sync_manual_off()
        if self.steam_ui:
            self._adv_title()

    def _sync_manual_off(self):
        ""


        off = SV.manual_off_shown(self.manual, self.route)
        if off and not self.manual_off.winfo_manager():
            hide_all_tips()
            self.sub_row.pack_forget()
            self.form_stage.pack_forget()
            self.manual_off.pack(side="top", fill="both", expand=True)
        elif not off and self.manual_off.winfo_manager():
            self.manual_off.pack_forget()
            self.sub_row.pack(side="top", fill="x", pady=(0, px(GAP + 2)))
            self.form_stage.pack(side="top", fill="both", expand=True)

    def _show_advanced(self, on):
        if on and not self.adv_box.winfo_manager():
            self.adv_box.pack(side="top", fill="x", pady=(px(GAP + 2), 0), after=self.cols)
        elif not on:
            self.adv_box.pack_forget()

    def _build_gate_fail_view(self):
        card = RoundFrame(self.stage, pad=16, outline="#5a2e24")
        self.views["gate_fail"] = card
        i = card.inner
        self.gf_title = self._label(i, "Wrong Exanima version", 13, T.ERROR, "semibold", wrap=W - 80)
        self.gf_title.pack(fill="x")
        self.gf_text = self._label(i, "", 9, T.TEXT, wrap=W - 80)
        self.gf_text.pack(fill="x", pady=(px(4), px(8)))

        self.gf_found = tk.Frame(i, bg=T.SURFACE)
        self.gf_found.pack(fill="x", pady=(0, px(10)))



        self.gf_how = self._label(i, "How to get it", 9, T.TEXT, "semibold")
        self.gf_how.pack(fill="x")
        steps = tk.Frame(i, bg=T.SURFACE)
        steps.pack(fill="x", pady=(px(2), px(10)))
        self.gf_steps = []
        for n in (1, 2, 3):
            r = tk.Frame(steps, bg=T.SURFACE)
            r.pack(fill="x", pady=(px(3), 0))
            num = self._label(r, "%d." % n, 9, T.ACCENT, "semibold", width=2)
            num.pack(side="left", anchor="n")
            text = self._label(r, "", 9, T.TEXT, wrap=W - 106)
            text.pack(side="left", fill="x", expand=True)
            self.gf_steps.append((num, text))


        row = tk.Frame(i, bg=T.SURFACE)
        row.pack(fill="x")
        self.gf_dot = Dot(row, T.ACCENT, size=10)
        self.gf_dot.pack(side="left", anchor="n", padx=(px(3), px(10)), pady=(px(4), 0))
        self.gf_status = self._label(row, "", 10, T.TEXT, "semibold", wrap=W - 110)
        self.gf_status.pack(side="left", fill="x", expand=True)
        self.gf_next = self._label(i, "", 9, T.MUTED, wrap=W - 110)
        self.gf_next.pack(fill="x", padx=(px(23), 0), pady=(px(2), 0))
        self.gf_ready = tk.Frame(i, bg=T.SURFACE)
        self.gf_ready_dir = None
        self.gf_bar = ProgressBar(i, height=8)

        area = tk.Frame(i, bg=T.SURFACE)
        area.pack(fill="x", pady=(px(12), 0))
        self.gf_cmd_area = area
        self._label(area, "The download command (%s copies it for you):" % DG.BUTTON, 8, T.MUTED, wrap=W - 80).pack(fill="x", pady=(0, px(3)))
        cmd = tk.Frame(area, bg=T.RAISED, highlightthickness=1, highlightbackground=T.BORDER)
        cmd.pack(fill="x")
        self.gf_cmd_box = cmd
        self.gf_cmd = tk.Entry(cmd, bg=T.RAISED, fg=T.ACCENT, font=(T.FONT_MONO, 8), relief="flat", bd=0, readonlybackground=T.RAISED)
        self.gf_cmd.pack(side="left", fill="x", expand=True, padx=(px(8), px(2)), pady=px(8))
        self.gf_copy_label = DG.COPY
        self.gf_cmd_text = ""
        self.gf_copy = RoundButton(cmd, DG.COPY, self._gf_copy_cmd, kind="ghost", height=26, size=9)
        self.gf_copy.pack(side="right", padx=(0, px(4)))

    def _fill_gate_fail(self, r):
        exp, build = r.get("expected", ""), r.get("buildid", "")
        self.gf_text.configure(text=DG.intro(exp, build, r.get("depot_size"), r.get("installed")))
        self.gf_how.configure(text=DG.heading(r.get("installed")))
        for (_num, text), step in zip(self.gf_steps, DG.steps(exp, r.get("depot_size"))):
            text.configure(text=step)
        found = r.get("found") or []
        lines = []
        if r.get("explicit"):
            e = r["explicit"]
            lines.append(("Given folder: %s  →  %s" % (elide(e.get("dir", ""), 46), e.get("what", "")), e.get("dir")))
            if r.get("alternative"):
                alt = r["alternative"].get("dir", "")
                lines.append(("A supported copy exists at %s: remove the folder / EXANIMA_EXE setting to use it." % elide(alt, 46), alt))
        for f in found[:3]:
            lines.append(("Found: %s  →  %s" % (elide(f.get("dir", ""), 46), f.get("what", "")), f.get("dir")))
        if not lines:
            lines.append(("No Exanima.exe was found in your Steam libraries.", None))
        self._path_rows(self.gf_found, lines, W - 80)
        self._dg_show(DG.Watcher(DG.update_first(r.get("installed"))).step({"ok": False}, None))
        cmd = r.get("download_command", "")
        self.gf_cmd.configure(state="normal")
        self.gf_cmd.delete(0, "end")
        self.gf_cmd.insert(0, cmd)
        self.gf_cmd.configure(state="readonly")
        self.gf_cmd_text = cmd
        self._set_copy_label(DG.COPY)

    def _gf_copy_cmd(self):
        if self.gf_cmd_text:
            self._copy(self.gf_cmd_text)
            self._flash(self.gf_copy, "Copied", self.gf_copy_label)

    def _set_copy_label(self, text):
        ""
        self.gf_copy_label = text
        self.gf_copy.configure_button(text=text)

    def _path_rows(self, box, rows, wrap):
        ""

        for w in box.winfo_children():
            w.destroy()
        for text, folder in rows:
            r = tk.Frame(box, bg=box.cget("bg"))
            r.pack(fill="x")
            lab = self._label(r, text, 8, T.MUTED, wrap=wrap - 24)
            lab.pack(side="left")
            if folder:
                Tooltip(lab, folder)
                ok = DG.folder_target(folder) is not None
                b = FolderIcon(r, lambda d=folder: self._open_folder(d), size=14)
                b.set(enabled=ok)
                b.pack(side="left", anchor="n", padx=(px(6), 0), pady=(px(1), 0))
                Tooltip(b, "Open this folder" if ok else "This folder no longer exists")

    def _open_folder(self, path):
        ""
        if not DG.open_folder(path):
            self.show_error("Could not open %s: the folder is not there any more." % (path or "the folder"))



    def _dg_start(self):
        ""

        self.dg = DG.Watcher(DG.update_first((self.gate or {}).get("installed")))
        self.dg_phase = None
        self.dg_free = None
        self.dg_old = []
        self.dg_busy = False
        self.dg_token += 1
        self._dg_actions("idle", None)
        self._dg_poll(self.dg_token)

    def _dg_poll(self, token):
        if token != self.dg_token or self.view != "gate_fail" or not hasattr(self.api, "depot_status"):
            return

        def done(r):
            if token != self.dg_token or self.view != "gate_fail":
                return
            res = self.dg.step(r, datetime.datetime.now())
            if r.get("ok"):
                self.dg_old = [d.get("dir") for d in (r.get("old") or []) if d.get("dir")]
            free = DG.free_label(r) if r.get("ok") else self.dg_free
            if not self.dg_busy:
                self._dg_show(res)
                if res["phase"] != self.dg_phase or free != self.dg_free:
                    self.dg_free = free
                    self._dg_actions(res["phase"], res)
            self.root.after(DG.POLL_MS, lambda: self._dg_poll(token))

        self.run_bg(lambda: self.api.depot_status(self.opts.game_dir), done)

    def _dg_show(self, res):
        color = {"ready": T.OK, "failed": T.ERROR, "mismatch": T.ERROR, "not_replaced": T.ERROR, "blocked": T.ERROR}.get(res["phase"], T.ACCENT)
        self.gf_dot.set(color)
        self.gf_status.configure(text=res["text"], fg=T.ERROR if color == T.ERROR else T.TEXT)

        self.gf_next.configure(text=res.get("next") or "")

        cur = DG.current_step(res["phase"])
        for n, (num, _text) in enumerate(self.gf_steps, 1):
            num.configure(fg=T.OK if n < cur else T.ACCENT if n == cur else T.MUTED)

        ready = res.get("ready_dir") if res["phase"] == "ready" else None
        if ready != self.gf_ready_dir:
            self.gf_ready_dir = ready
            self._path_rows(self.gf_ready, [("New copy: %s" % elide(ready, 46), ready)] if ready else [], W - 110)
        if ready and not self.gf_ready.winfo_manager():
            self.gf_ready.pack(fill="x", padx=(px(23), 0), pady=(px(4), 0), before=self.gf_cmd_area)
        elif not ready:
            self.gf_ready.pack_forget()
        if res["phase"] == "downloading" and res["progress"] is not None:
            if not self.gf_bar.winfo_manager():
                self.gf_bar.pack(fill="x", pady=(px(8), 0), before=self.gf_cmd_area)
            self.gf_bar.set(res["progress"])
        else:
            self.gf_bar.pack_forget()

    def _dg_actions(self, phase, res):
        self.dg_phase = phase

        free = getattr(self, "dg_free", None)
        secondary = (free, self._dg_free_space, True) if free and phase != "downloading" else None
        if DG.main_button(phase) == "install":
            self.set_actions(primary=("Install the mod into it", lambda: self._dg_install(res["ready_dir"]), True), secondary=secondary)
        else:

            self.set_actions(primary=(DG.BUTTON, self._downgrade, True), secondary=secondary)

    def _downgrade(self):
        ""




        if getattr(self, "dg_busy", False):
            return
        prepare = getattr(self.api, "depot_prepare", None)
        if prepare is None or not DG.move_aside_first(self.dg_phase):
            self._dg_console(None)
            return
        self.dg_busy = True
        self.set_actions(primary=(DG.BUTTON, None, False))

        def done(r):
            self.dg_busy = False
            go, text = DG.prepare_outcome(r)
            if not go:
                if self.dg is not None:
                    self.dg.blocked(text)
                    res = self.dg.step({"ok": False}, datetime.datetime.now())
                    self._dg_show(res)
                    self._dg_actions(res["phase"], res)
                return
            self._dg_console(text)

        self.run_bg(prepare, done)

    def _dg_console(self, note):
        ""
        cmd = (self.gate or {}).get("download_command", "")
        if cmd:
            self._copy(cmd)
            self._set_copy_label(DG.COPY_AGAIN)
        if note:
            self.show_info(note)
        if self.dg is not None:
            self.dg.clicked(datetime.datetime.now())
            res = self.dg.step({"ok": False}, datetime.datetime.now())
            self._dg_show(res)
            self._dg_actions(res["phase"], res)
        self.run_bg(self.api.open_steam_console, lambda r: None)

    def _dg_free_space(self):
        ""
        dirs = list(getattr(self, "dg_old", []) or [])
        if not dirs or not hasattr(self.api, "depot_remove_old"):
            return
        shown = "\n".join(elide(d, 70) for d in dirs[:4]) + ("\n…" if len(dirs) > 4 else "")
        if not messagebox.askyesno(AB.PRODUCT_NAME, "Delete the old Exanima copies the launcher moved aside before the download?\n\n%s\n\n%s\n\n"
                                   "Only those old copies are deleted: your normal Exanima install, the new copy and your saves stay where they are." % (shown, self.dg_free or ""), parent=self.root):
            return

        def work():
            freed, errors = 0, []
            for d in dirs:
                r = self.api.depot_remove_old(d)
                if r.get("ok"):
                    freed += int(r.get("freed") or 0)
                else:
                    errors.append(r.get("error") or d)
            return {"ok": not errors, "freed": freed, "errors": errors}

        def done(r):
            if r.get("ok"):
                self.show_info("Freed %s." % DG.gb(r.get("freed") or 0), "ok")
            else:
                self.show_error("Some old copies could not be removed (%s). Close anything using them and try again." % "; ".join(r.get("errors") or [r.get("error") or "unknown"])[:300])

        self.run_bg(work, done)

    def _dg_install(self, game_dir):
        ""

        self.dg_token += 1
        self.set_actions(primary=("Installing…", None, False))

        def done(r):
            self._check_game()
            if r.get("ok"):
                self.show_info("Installed into %s. Your normal Exanima install is untouched." % game_dir, "ok")
            else:
                self.show_failure(r, "install", r.get("error") or "The install failed.")

        self.run_bg(lambda: self.api.install(game_dir), done)




    def _on_mode(self, m):
        self.mode = m
        self.clear_banner()
        self._show_mode()

    def _show_mode(self):
        if self.connecting:
            self._set_connecting(False)
        self.tabs.set(self.mode)
        self._lock_tabs(False)
        if self.gate and self.gate.get("ok"):


            self._form_chrome(True)
        self._show_checks(True)
        self._show_advanced(True)
        self._sync_route_ui()
        if self.mode == "host":
            self._show_view("host")
            self._refresh_host_addr()
            self._update_start()
        else:
            self._show_view("join")
            self._update_start()

    def _back_to_form(self):
        self.downloading = False
        self._stop_waiting()
        if self.gate and self.gate.get("ok"):
            self._form_chrome(True)
            if self.pending_invite:

                (lobby, after), self.pending_invite = self.pending_invite, None
                if self._apply_invite(lobby, after):
                    return
            self._show_mode()




    def _apply_invite(self, lobby, after_game):
        ""
        invite = SV.invite_code(self.steam_ui, lobby)
        if not invite:
            return False
        self.opts.after_game = after_game
        self.mode = "join"
        self._set_route(SV.ROUTE_STEAM, sync=False)
        self.v_code.set(invite)
        self._show_mode()
        if SV.game_still_open(self.opts.after_game, self.api.process_alive):
            self.show_info(SV.INVITE_FROM_GAME)
        else:
            self.show_info(SV.INVITE_READY)
        return True

    def _poll_inbox(self):
        ""

        if self._closing:
            return
        try:
            if self.steam_ui and self.api is not None:
                g = self.game or {}
                mine = g.get("pid")
                got = HO.take_invites(self.inbox, lambda after, age: HO.should_take(after, mine, self.gui_slot, age))
                if got:
                    self._on_invite(*got[-1])
        except Exception:
            log_error(traceback.format_exc())
        self.root.after(HO.POLL_MS, self._poll_inbox)

    def _on_invite(self, lobby, after_game):
        if after_game:
            self.api.process_alive(after_game)
        self.pending_invite = (lobby, after_game)
        g = self.game
        if g and g.get("pid") and self.api.process_alive(g["pid"]):


            self.show_info(SV.INVITE_WAITS_FOR_GAME)
            return
        self._take_pending_invite()

    def _take_pending_invite(self):
        ""


        if not self.pending_invite or not (self.gate and self.gate.get("ok")):
            return
        if self.view in ("host", "join") and not self.connecting:
            self._back_to_form()
        elif self.view == "running" and not self.game:
            self._back_to_form()
        else:
            self.show_info(SV.INVITE_AFTER_THIS)
            return
        self._restore_window()

    def _flow_mode(self):
        ""
        self._form_chrome(False)
        self._show_checks(False)
        self._show_advanced(False)

    def _on_host_info(self, r):


        self.host_info = r if r.get("ok") else {"lan_ips": [], "port": 27500}
        self._refresh_addresses()

    def _name(self):


        return S.clean_name(self.v_name.get())

    def _name_blocked(self):
        ""
        problem = S.launcher_name_problem(self.v_name.get())
        if problem is None:
            return False
        self.show_error("Your name: " + problem)
        field = self.f_name_host if self.mode == "host" else self.f_name_join
        field.entry.focus_set()
        return True

    def _common_opts(self):
        o = {"name": self._name(), "console": bool(self.v_console.get()), "allow_inject": self.opts.allow_inject}
        if DEV:
            o.update(DEV.launch_opts(self.opts.debug_tools))
        level = log_level_for(self.opts.log_level, bool(self.v_detailed.get()))
        if level:
            o["log_level"] = level
        if self.v_tile.get():
            o["window"] = "auto"
        if self.opts.game_dir:
            o["game_dir"] = self.opts.game_dir
        elif self.gate and self.gate.get("dir"):
            o["game_dir"] = self.gate["dir"]
        return o




    def _start_host(self):
        self.clear_banner()
        if not SV.connect_possible(self.steam_ui, self.steam_enabled, self.manual, self.route):

            self.show_error(SV.greyed_note(self.route, self.steam_note, self.manual_note) or SV.MANUAL_OFF)
            return
        if not self._host_pw_ok():


            self.show_error("Type a lobby password or press Generate first: friends need it to join.")
            self.f_host_pw.entry.focus_set()
            return
        if self._name_blocked():
            return
        self.save_settings()
        self._ensure_installed(self._do_start_host)

    def _do_start_host(self):
        direct = bool(self.v_host_direct.get())

        self.host_steam = SV.host_through_steam(self.steam_ui, direct)
        self.host_access = SV.access_value(self.access)
        self.host_code = None

        self.host_portmap = bool(self.v_open_port.get()) and DV.open_port_applies(self.steam_ui, direct)

        password = "" if self.host_steam else self.v_host_pw.get()
        opts = dict(self._common_opts(), players=self.players, password=password, **SV.host_extra_opts(self.steam_ui, direct, self.access))
        self._flow_mode()
        self._show_running("host")
        self.run_bg(lambda: self.api.start_host(opts), lambda r: self._on_started(r, "host"))




    def _connect(self):
        self.clear_banner()


        r = SV.join_route(self.steam_ui, bool(self.v_join_direct.get()), self.v_code.get(), self.v_addr.get(), self.v_join_pw.get(), self.manual)
        if r.kind == "error":
            self.show_error(r.error)
            field = {"code": self.f_code, "addr": self.f_addr}[r.field]
            if r.field == "code":
                field.set_error(True)
            field.entry.focus_set()
            self.scroll.see(field)
            return
        if self._name_blocked():
            return
        if r.kind == "steam":

            still = SV.game_still_open(self.opts.after_game, self.api.process_alive)
            if still:
                self.show_error(still)
                return
            self.opts.after_game = None
            self._steam_join(r.address)
            return
        self._manual_join(r.address)

    def _manual_join(self, addr):
        ""






        self.save_settings()
        self.repick = None
        self.roster_addr = None
        self._lock_tabs(True)
        self.set_actions(primary=("Connecting…", None, False))
        self._set_connecting(True)
        self._ensure_installed(lambda: self._do_play_new(dict(NEW_CHARACTER, menu_join=True), manual_addr=addr))

    def _steam_join(self, addr):
        ""




        self.save_settings()
        self.repick = None
        self.roster_addr = None
        self._lock_tabs(True)
        self.set_actions(primary=("Connecting…", None, False))
        self._set_connecting(True)
        self._ensure_installed(lambda: self._do_play_new(dict(NEW_CHARACTER, steam=True), addr=addr))

    def _set_connecting(self, on):
        ""

        self.connecting = bool(on)
        for field in (self.f_name_host, self.f_name_join):
            field.set_enabled(not on)
        self.route_seg.set_enabled(not on)



    def _fetch_roster(self, addr=None):
        addr = addr or self.roster_addr or self.v_addr.get().strip()
        pw, name = self.v_join_pw.get(), self._name()
        token = self.wait_token
        self.run_bg(lambda: self.api.fetch_roster(addr, pw, name), lambda r: self._on_roster(r, token))

    def _on_roster(self, r, token=None):
        if token is not None and token != self.wait_token:
            return
        self._set_connecting(False)
        self._lock_tabs(False)
        if not r.get("ok"):
            self._stop_waiting()
            self._show_mode()
            if r.get("kind") != "cancelled":
                self.show_error(r.get("error", "The host did not answer."))
            if r.get("kind") in ("name", "bad_name"):

                self.f_name_join.set_error(True)
                self.f_name_join.entry.focus_set()
            return
        self.roster_addr = r.get("addr")
        if r.get("pending"):

            self._show_waiting(r)
            return
        self._stop_waiting()



        self._show_roster(r)
        if self.repick is not None:

            self.show_info("The host started a new game, so the list of bodies changed. Pick yours again.")

    def _show_roster(self, r, keep_id=None, keep_user=False):
        ""


        self.roster = r
        self._flow_mode()
        self._fill_roster(r, keep_id, keep_user)
        self._show_view("roster")
        self.set_actions(primary=("Play", self._play, self.selected is not None), secondary=("Back", self._back_to_form))
        self._watch_own_body()

    def _watch_own_body(self):
        ""




        self.list_token += 1
        if self.view != "roster" or not P.held_by_name(self.roster, self._name()):
            return
        token = self.list_token
        self.root.after(ROSTER_REFRESH_MS, lambda: self._refresh_list(token))

    def _refresh_list(self, token):
        if token != self.list_token or self.view != "roster":
            return
        addr, pw, name = self.roster_addr or self.v_addr.get().strip(), self.v_join_pw.get(), self._name()
        self.run_bg(lambda: self.api.fetch_roster(addr, pw, name), lambda r: self._on_list_refresh(r, token))

    def _on_list_refresh(self, r, token):
        if token != self.list_token or self.view != "roster":
            return
        if not r.get("ok") or r.get("pending") or P.same_bodies(r, self.roster):


            self.list_token += 1
            token = self.list_token
            self.root.after(ROSTER_REFRESH_MS, lambda: self._refresh_list(token))
            return

        keep = (self.selected or {}).get("char_id")
        by_user = getattr(self, "selected_by_user", False)
        if keep == 0 and not by_user:
            keep = None


        self._show_roster(r, keep_id=keep, keep_user=by_user)

    def _show_waiting(self, r):
        self._flow_mode()
        if self.view != "waiting":
            self._show_view("waiting")
            self.wait_spin.start()
        host = r.get("host_name") or "The host"
        why = r.get("level") or ""
        self.wait_sub.configure(text="%s: %s." % (host, why) if why else "%s is not in the game yet." % host)
        self.set_actions(primary=("Waiting…", None, False), secondary=("Cancel", self._cancel_waiting))
        self.waiting = True
        self.wait_token += 1
        token = self.wait_token
        self.root.after(ROSTER_POLL_MS, lambda: self._poll_roster(token))

    def _poll_roster(self, token):
        if self.waiting and token == self.wait_token and self.view == "waiting":
            self._fetch_roster()

    def _stop_waiting(self):
        self.waiting = False
        self.wait_token += 1
        self.wait_spin.stop()

    def _cancel_waiting(self):
        self._stop_waiting()
        self.api.cancel()
        self.repick = None
        self._back_to_form()

    def _fill_roster(self, r, keep_id=None, keep_user=False):
        ""


        for w in self.ro_list.winfo_children():
            w.destroy()
        self.selected = None
        host, level = r.get("host_name") or "The host", r.get("level") or ""
        self.ro_sub.configure(text="%s is %s." % (host, ("in " + level) if level else "in the menu"))
        bodies = r.get("bodies") or []

        last_name = (self.repick or {}).get("name") or self.s["last_body"].get(self.roster_addr or "")
        pre = P.preselect(r, last_name)
        rows = []

        new_row = BodyRow(self.ro_list, dict(NEW_CHARACTER), self._select_row, self._activate_row)
        new_row.pack(fill="x", pady=(0, px(6)))
        rows.append(new_row)
        for b in bodies:
            used = bool(last_name) and (b.get("name") or "").strip().lower() == last_name.strip().lower()
            row = BodyRow(self.ro_list, b, self._select_row, self._activate_row, last_used=used)
            row.pack(fill="x", pady=(0, px(6)))
            rows.append(row)
        self.ro_rows = rows
        free = [row for row in rows if row.free]
        kept = next((row for row in free if keep_id is not None and row.body.get("char_id") == keep_id), None)
        pick = kept or next((row for row in free if pre is not None and row.body.get("char_id") == pre.get("char_id")), None)
        pick = pick or new_row
        if pick:


            self._select_row(pick, user=bool(keep_user and pick is kept))
        if not bodies:
            self.ro_note.configure(text="No characters on the host yet: choose New character, then press CREATE in the game. New characters can join only when the host starts a new game.")
        elif P.held_by_name(r, self._name()):

            self.ro_note.configure(text="A body is still in use under your name, probably by your last game. The host frees it "
                                        "a few seconds after that game has closed; this list updates by itself.")
        elif len(free) <= 1:
            self.ro_note.configure(text="No character of yours is free: New character starts the game at its main menu (CREATE makes one; new characters can join only when the host starts a new game).")
        else:
            self.ro_note.configure(text="Double-click a character to play it right away. New character: make one in the game with CREATE.")

    def _select_row(self, row, user=True):
        for r in self.ro_rows:
            r.set_selected(r is row)
        self.selected = row.body


        self.selected_by_user = user
        self.set_actions(primary=("Play", self._play, True), secondary=("Back", self._back_to_form))

    def _activate_row(self, row):
        self._select_row(row)
        self._play()

    def _play(self):
        if not self.selected:
            return
        self.clear_banner()
        body = self.selected
        self.repick = None
        self._ensure_installed(lambda: self._do_play(body))

    def _do_play(self, body):
        if not body.get("char_id"):
            self._do_play_new(body)
            return
        if self.roster_addr and body.get("name"):
            self.s["last_body"][self.roster_addr] = body["name"]
        self.save_settings()
        opts = dict(self._common_opts(), addr=self.roster_addr or self.v_addr.get().strip(), password=self.v_join_pw.get(), char_id=body["char_id"],
                    direct=True)
        self._flow_mode()
        self.local_copy = None
        self.pr_title.configure(text="Downloading the host's save")
        self.pr_sub_base = "Playing as %s  ·  host %s" % (body_title(body), opts["addr"])
        self.pr_sub.configure(text=self.pr_sub_base)
        self.pr_bar.indeterminate()
        self.pr_bytes.configure(text="")
        self.pr_pct.configure(text="")
        self.pr_status.configure(text="Asking the host for its save (the host writes it now)…")
        self._show_view("progress")
        self.set_actions(primary=("Play", None, False), secondary=("Cancel", self.api.cancel))
        self.downloading = True

        def progress(received, total, text):
            self.q.put((self._on_progress, (received, total, text)))

        def work():
            r = self.api.download_save(opts, progress)
            if not r.get("ok"):
                return r
            self.q.put((self._on_downloaded, r))



            return self.api.start_join(dict(opts, world=r.get("world"), instance=r.get("instance"), token=r.get("token")))

        self.run_bg(work, lambda r: self._on_started(r, "join", body))

    def _do_play_new(self, body, addr=None, manual_addr=None):
        ""



        self.save_settings()

        opts = dict(self._common_opts(), addr=addr or manual_addr or self.roster_addr or self.v_addr.get().strip(), password="" if addr else self.v_join_pw.get(),
                    char_id=0, direct=addr is None)
        self._flow_mode()
        self._show_running("join", body)
        self.run_bg(lambda: self.api.start_join(opts), lambda r: self._on_started(r, "join", body))

    def _on_progress(self, p):
        received, total, text = p
        if not self.downloading:
            return
        n = P.local_copy_of(text)
        if n:
            self._set_local_copy(n)


        if not total and text and "still starting the game" in text:
            if self.view != "waiting":
                self._show_view("waiting")
                self.wait_spin.start()
            self.wait_sub.configure(text=text)
            self.set_actions(primary=("Waiting…", None, False), secondary=("Cancel", self.api.cancel))
            return
        if self.view == "waiting":
            self.wait_spin.stop()
            self._show_view("progress")
            self.set_actions(primary=("Play", None, False), secondary=("Cancel", self.api.cancel))
        if total:
            self.pr_bar.set(received / float(total))
            self.pr_bytes.configure(text="%s of %s" % (fmt_mb(received), fmt_mb(total)))
            self.pr_pct.configure(text="%d%%" % int(100 * received / total))
        if text:
            self.pr_status.configure(text=text)

    def _set_local_copy(self, n):
        ""
        self.local_copy = n
        self.pr_sub.configure(text="%s  ·  local copy %d" % (getattr(self, "pr_sub_base", ""), n))

    def _on_downloaded(self, r):
        self.downloading = False
        self.pr_bar.set(1.0)
        self.pr_pct.configure(text="100%")
        inst = r.get("instance") or 1
        if inst >= 2:
            self._set_local_copy(inst)
        self.pr_status.configure(text="Save installed (slot %s). Starting %s…" % (r.get("slot"), "local copy %d" % inst if inst >= 2 else "the game"))
        self.set_actions(primary=("Play", None, False), secondary=("Cancel", None, False))




    def _show_running(self, mode, body=None):
        self._run_state(True)
        self.run_title.configure(text="Starting the game…")
        self.run_sub.configure(text="Exanima is starting with the co-op mod.")
        self.run_log.configure(text="")
        self.run_port_note.configure(text="")
        self.run_port_note.pack_forget()
        if self.run_code_box is not None:
            self.run_code_box.pack_forget()
            self.run_code_note.pack_forget()
            self._run_code_shown = None
        if mode == "host" and self.host_steam:


            self.run_addr_box.pack_forget()
            self.run_pw_box.pack_forget()
            self.run_code_box.pack(fill="x", before=self.run_log)
            self._refresh_run_code()
        elif mode == "host":
            self.run_addr_box.pack(fill="x", before=self.run_log)
            self._refresh_run_addr()
            self._ensure_router_check()
            self.run_pw_box.pack(fill="x", before=self.run_log)
            self._refresh_run_pw(self.f_host_pw.revealed)
        else:
            self.run_addr_box.pack_forget()
            self.run_pw_box.pack_forget()
        self._show_view("running")
        self.set_actions(primary=("Close launcher", None, False))

    def _on_started(self, r, mode, body=None):
        self.downloading = False
        if not r.get("ok"):
            if mode == "join" and r.get("kind") == "stale_body":



                if self.repick is None:
                    self.repick = {"name": (body or {}).get("name") or ""}
                self.clear_banner()
                self._show_waiting({"host_name": (self.roster or {}).get("host_name"), "level": "the host started a new game; its bodies changed"})
                return
            if mode == "join" and r.get("kind") == "cancelled" and self.roster:


                self._show_roster(self.roster, keep_id=(body or {}).get("char_id"), keep_user=True)
                return
            self._back_to_form()
            if r.get("kind") == "not_installed":
                self._refresh_install()
            if r.get("kind") != "cancelled":
                self.show_failure(r, "start", r.get("error", "The game could not be started."))
            return
        if self.view != "running":
            self._show_running(mode, body)


        self.game = {"pid": r.get("pid"), "log": r.get("log"), "pos": r.get("log_from", 0), "mode": mode, "lines": [], "outcome": None, "since": time.time(),
                     "new": bool(mode == "join" and (body or {}).get("new")), "progressed": False,
                     "steam": bool(mode == "host" and self.host_steam), "steam_join": bool(mode == "join" and (body or {}).get("steam")),

                     "menu_join": bool(mode == "join" and ((body or {}).get("steam") or (body or {}).get("menu_join")))}
        warn = [l[2:] for l in r.get("lines", []) if l.startswith("! ")]
        self._run_state(False, T.OK)
        self.run_title.configure(text="Game running")
        if mode == "host" and self.host_steam:
            self.run_sub.configure(text="Load your co-op save with CONTINUE, or BEGIN a new game. Friends can join once you are in a level: "
                                        "from their Steam friends list (Join Game), with the join code below, or by your invite (F1 in the game).")
            self._refresh_run_code()
        elif mode == "host":
            self.run_sub.configure(text="Load your co-op save with CONTINUE, or BEGIN a new game. Friends can join once you are in a level, with your address and the password below.")
        else:
            inst = r.get("instance") or 1
            copy = "  (local copy %d)" % inst if inst >= 2 else ""
            if (body or {}).get("steam"):

                self.run_sub.configure(text="The game starts at its main menu and joins the host through Steam. There, CREATE makes a new "
                                            "character (only when the host starts a new game) and POSSESS plays your own.")
            elif (body or {}).get("menu_join"):

                self.run_sub.configure(text="The game starts at its main menu and joins the host%s. There, CREATE makes a new "
                                            "character (only when the host starts a new game) and POSSESS plays your own." % copy)
            elif (body or {}).get("new"):
                self.run_sub.configure(text="New character%s: the game starts at its main menu. Press CREATE there to make your character (the line under the menu title says when you can)." % copy)
            else:
                self.run_sub.configure(text="Joining as %s%s. In the game, choose CONTINUE if it does not load by itself." % ((body or {}).get("name", "your body"), copy))
            self._run_state(True)
            self.run_title.configure(text="Joining…")
        if warn:
            self.show_error(" ".join(warn))
        self.set_actions(primary=("Close launcher", self._ask_close, True))
        if mode == "host" and self.host_portmap and self.api is not None:


            self.game["portmap"] = True
            self._start_portmap(int((self.host_info or {}).get("port") or 27500))



        close = bool(self.v_close.get()) and not DV.keep_launcher_open(self.game.get("portmap"))
        action = L.after_start(close, bool(warn), wait_for_code=bool(self.game.get("steam")))
        if action == "wait_code":
            self.game["code_wait"] = True
            self.game["settled_at"] = None
        if action == "close":
            self._on_close()
            return
        if action == "minimize":
            self.hid_for_game = True
            self.root.iconify()
        self.root.after(800, self._poll_game)

    def _restore_window(self):
        ""



        hid, self.hid_for_game = self.hid_for_game, False
        if self._closing:
            return
        if hid or self._hidden():
            self.root.deiconify()
            self.root.lift()
            self._fit_soon()

    def _code_wait_over(self, g):
        ""

        now = time.time()
        settled = SV.host_code_done(self.host_code)
        if settled and g.get("settled_at") is None:
            g["settled_at"] = now
        act = L.after_code_wait(bool(self.v_close.get()), settled, now - g["since"], now - (g.get("settled_at") or now))
        if not act:
            return False
        g["code_wait"] = False
        if act == "close":
            self._on_close()
            return True
        self.hid_for_game = True
        self.root.iconify()
        return False

    def _refresh_run_port(self, st):
        ""

        port = int((self.host_info or {}).get("port") or 27500)
        text, bad = DV.port_note(st, port)
        if text == self.run_port_note.cget("text"):
            return
        self.run_port_note.configure(text=text, fg=T.ACCENT if bad else T.DIM)
        if text and not self.run_port_note.winfo_manager():
            if self.run_addr_box.winfo_manager():
                self.run_port_note.pack(fill="x", pady=(0, px(8)), after=self.run_addr_box)
            else:
                self.run_port_note.pack(fill="x", pady=(0, px(8)), before=self.run_log)
        elif not text:
            self.run_port_note.pack_forget()
        self._fit_soon()

    def _poll_game(self):
        g = self.game
        if not g or self.view != "running" or self._closing:
            return
        if g.get("steam") and g.get("pid"):



            try:
                st = self.api.host_status(g.get("log") or "", g["pid"])
            except Exception:
                st = None
            self.host_code = SV.merge_host_status(self.host_code, st)
            self._refresh_run_code()
            if g.get("code_wait") and self._code_wait_over(g):
                return
        if g.get("portmap") and self.portmap_live:

            try:
                st = self.api.portmap_status()
            except Exception:
                st = None
            self._refresh_run_port(st)
        if g["mode"] == "join" and g["outcome"] is None and g.get("log"):
            st = self.api.join_status(g["log"], g["pos"])
            g["pos"] = st.get("pos", g["pos"])
            new_lines = st.get("lines", [])
            g["lines"] = (g["lines"] + new_lines)[-5:]
            self.run_log.configure(text="\n".join(g["lines"]))
            if g.get("new") and not g.get("progressed") and any(L.join_progress_line(l) for l in new_lines):


                g["progressed"] = True
                self.run_title.configure(text="At the game's main menu")
                if g.get("menu_join"):
                    self.run_sub.configure(text="Press CREATE there for a new character, or POSSESS for your own. The game loads by itself once the host is ready.")
                else:
                    self.run_sub.configure(text="Press CREATE there to make your character. Once the host has made it, the game loads by itself.")
            if st.get("outcome") == "joined":
                g["outcome"] = "joined"
                self._run_state(False, T.OK)
                self.run_title.configure(text="Joined. Have fun.")
            elif st.get("outcome") == "refused":
                g["outcome"] = "refused"
                self._run_state(False, T.ERROR)
                self.run_title.configure(text="The host refused the join")
                self.run_sub.configure(text="The game window's title says why. Close the game and try again.")
            elif st.get("outcome") == "full":

                g["outcome"] = "full"
                self._run_state(False, T.ERROR)
                self.run_title.configure(text="The session is full")
                self.run_sub.configure(text="Try again later.")
            elif L.join_timed_out(g.get("new"), time.time() - g["since"], g.get("progressed")):
                g["outcome"] = "timeout"
                self._run_state(False, T.ACCENT)
                self.run_title.configure(text="Game running")
                self.run_sub.configure(text="No join result within 3 minutes; see the console window or the log.")
            if L.restore_on_outcome(g["outcome"]):


                self._restore_window()
        if g.get("pid") and not self.api.process_alive(g["pid"]):
            self._run_state(False, T.DIM)
            self.run_title.configure(text="The game has closed")
            self.run_sub.configure(text="Start again whenever you like.")
            if g.get("steam") and self.run_code_box is not None:

                self.run_code_box.pack_forget()
                self.run_code_note.pack_forget()
            if g.get("portmap"):

                self.run_port_note.pack_forget()
                self._stop_portmap_soon()
            self.game = None
            self.set_actions(primary=("Back", self._back_to_form, True), secondary=("Close", self._on_close))
            self._restore_window()
            self._take_pending_invite()
            return

        self.root.after(L.poll_ms(self._hidden()), self._poll_game)


def _end_portmap(api, starter, wait_ms):
    ""

    if starter is not None:
        starter.join(wait_ms / 1000.0 + 1.0)
    try:
        api.portmap_stop(wait_ms)
    except Exception:
        pass


def hand_over_invite(opts):
    ""


    if opts.join_lobby is None:
        return False
    try:
        folder = HO.inbox_dir(os.path.dirname(S.settings_path()))
        return HO.hand_over(folder, opts.join_lobby, opts.after_game, S.held_gui_slots())
    except Exception:
        log_error(traceback.format_exc())
        return False


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    opts = Options(argv)
    if hand_over_invite(opts):
        return 0
    T.enable_dpi_awareness()
    T.set_app_id()
    root = tk.Tk()
    App(root, opts)
    root.mainloop()
    return 0
