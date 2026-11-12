""

import ctypes
import tkinter as tk
from tkinter import ttk


BG = "#141311"
SURFACE = "#1c1a17"
RAISED = "#26231f"
HOVER = "#2e2a25"
BORDER = "#36312b"
TEXT = "#ece4d6"
MUTED = "#a39a8c"
DIM = "#6f675c"
ACCENT = "#d9a441"
ACCENT_HI = "#e8b957"
ACCENT_LO = "#b9892f"
ON_ACCENT = "#1b150c"
OK = "#8cbf6e"
ERROR = "#e0735a"
ERROR_BG = "#2b1c17"
INFO_BG = "#22201b"







FOLDER = "#36312a"
FOLDER_EDGE = "#5a5249"
FOLDER_DIM = "#8a8174"
WELL = "#131210"


def well_for(bg):
    ""
    return WELL if bg == FOLDER else RAISED


def dim_for(bg):
    ""
    return FOLDER_DIM if bg == FOLDER else DIM

FONT = "Segoe UI"
FONT_SEMI = "Segoe UI Semibold"
FONT_TITLE = "Cambria"
FONT_MONO = "Consolas"

_scale = 1.0



SCALE_OVERRIDE = None
WORK_OVERRIDE = None


dpi_mode = "unaware"


def enable_dpi_awareness():
    ""


    global dpi_mode
    try:
        f = ctypes.windll.user32.SetProcessDpiAwarenessContext
        f.argtypes = [ctypes.c_ssize_t]
        f.restype = ctypes.c_int
        if f(-4):
            dpi_mode = "per-monitor-v2"
            return dpi_mode
    except Exception:
        pass
    for level, name in ((2, "per-monitor"), (1, "system")):
        try:
            if ctypes.windll.shcore.SetProcessDpiAwareness(level) == 0:
                dpi_mode = name
                return dpi_mode
        except Exception:
            pass
    try:
        if ctypes.windll.user32.SetProcessDPIAware():
            dpi_mode = "system"
    except Exception:
        pass
    return dpi_mode


class _RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


class _MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong), ("rcMonitor", _RECT), ("rcWork", _RECT), ("dwFlags", ctypes.c_ulong)]


class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def _monitor(hwnd=None):
    ""
    try:
        u = ctypes.windll.user32
        u.MonitorFromWindow.restype = ctypes.c_void_p
        u.MonitorFromPoint.restype = ctypes.c_void_p
        if hwnd:
            return u.MonitorFromWindow(ctypes.c_void_p(hwnd), 2)
        pt = _POINT()
        u.GetCursorPos(ctypes.byref(pt))
        return u.MonitorFromPoint(pt, 2)
    except Exception:
        return None


def monitor_dpi(hwnd=None):
    ""
    try:
        mon = _monitor(hwnd)
        x, y = ctypes.c_uint(), ctypes.c_uint()
        if mon and ctypes.windll.shcore.GetDpiForMonitor(ctypes.c_void_p(mon), 0, ctypes.byref(x), ctypes.byref(y)) == 0 and x.value:
            return int(x.value)
    except Exception:
        pass
    return 96


def work_area(hwnd=None):
    ""
    if WORK_OVERRIDE:
        return tuple(WORK_OVERRIDE)
    try:
        mon = _monitor(hwnd)
        mi = _MONITORINFO()
        mi.cbSize = ctypes.sizeof(_MONITORINFO)
        if mon and ctypes.windll.user32.GetMonitorInfoW(ctypes.c_void_p(mon), ctypes.byref(mi)):
            r = mi.rcWork
            return (r.left, r.top, r.right, r.bottom)
    except Exception:
        pass
    try:
        r = _RECT()
        if ctypes.windll.user32.SystemParametersInfoW(0x30, 0, ctypes.byref(r), 0):
            return (r.left, r.top, r.right, r.bottom)
    except Exception:
        pass
    return (0, 0, 1280, 680)


def window_handle(root):
    try:
        return ctypes.windll.user32.GetParent(root.winfo_id()) or None
    except Exception:
        return None


def fit_window(natural_h, width, work, scale, pos=None):
    ""





    left, top, right, bottom = work
    ww, wh = right - left, bottom - top
    margin = int(round(8 * scale))
    chrome_w = int(round(16 * scale))
    chrome_h = int(round(40 * scale))
    w = min(width, max(1, ww - chrome_w - 2 * margin))
    avail = max(1, wh - chrome_h - 2 * margin)
    h = min(natural_h, avail)
    scrolls = natural_h > avail
    if pos is None:
        x = left + (ww - (w + chrome_w)) // 2
        y = top + margin if scrolls else top + (wh - (h + chrome_h)) // 2
    else:
        x, y = pos

    x = max(left, min(x, right - (w + chrome_w)))
    y = max(top, min(y, bottom - margin - (h + chrome_h)))
    return x, y, w, h, scrolls


def set_app_id(app_id="ExanimaCoop.Launcher"):
    ""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(ctypes.c_wchar_p(app_id))
    except Exception:
        pass


def init_scale(root):
    ""

    global _scale
    if SCALE_OVERRIDE:
        s = float(SCALE_OVERRIDE)
    else:
        dpi = monitor_dpi() if dpi_mode.startswith("per-monitor") else None
        if not dpi or dpi == 96:
            try:
                dpi = float(root.winfo_fpixels("1i"))
            except Exception:
                dpi = 96.0
        s = max(1.0, dpi / 96.0)
    try:
        root.tk.call("tk", "scaling", s * 96.0 / 72.0)
    except Exception:
        pass
    _scale = s
    return _scale


def px(n):
    ""
    return int(round(n * _scale))


def font(size=10, weight="normal", family=None):
    fam = family or (FONT_SEMI if weight == "semibold" else FONT)
    return (fam, size, "bold" if weight == "bold" else "normal")


def dark_title_bar(root):
    ""
    try:
        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        on = ctypes.c_int(1)
        for attr in (20, 19):
            if ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(on), ctypes.sizeof(on)) == 0:
                break

        color = ctypes.c_int(0x00111314)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(color), ctypes.sizeof(color))
    except Exception:
        pass


def make_icon(size=64):
    ""
    img = tk.PhotoImage(width=size, height=size)
    c = (size - 1) / 2.0
    rows = []
    for y in range(size):
        row = []
        for x in range(size):
            d = abs(x - c) + abs(y - c)
            if d <= c * 0.95:
                inner = d <= c * 0.42
                edge = d > c * 0.80
                row.append("#1b150c" if inner else (ACCENT_LO if edge else ACCENT))
            else:
                row.append(BG)
        rows.append("{" + " ".join(row) + "}")
    img.put(" ".join(rows))
    return img


def setup_ttk(root):
    ""
    st = ttk.Style(root)
    try:
        st.theme_use("clam")
    except tk.TclError:
        pass
    st.configure(
        "Dark.TCombobox",
        fieldbackground=RAISED,
        background=RAISED,
        foreground=TEXT,
        arrowcolor=ACCENT,
        bordercolor=BORDER,
        lightcolor=RAISED,
        darkcolor=RAISED,
        selectbackground=RAISED,
        selectforeground=TEXT,
        padding=(px(8), px(6)),
        arrowsize=px(14),
    )
    st.map(
        "Dark.TCombobox",
        fieldbackground=[("readonly", RAISED), ("disabled", SURFACE)],
        foreground=[("disabled", DIM)],
        bordercolor=[("focus", ACCENT), ("hover", "#4a443c")],
        arrowcolor=[("disabled", DIM)],
        background=[("active", HOVER), ("pressed", HOVER)],
    )

    st.configure("Compact.Dark.TCombobox", padding=(px(8), px(3)))
    root.option_add("*TCombobox*Listbox.background", RAISED)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", ON_ACCENT)
    root.option_add("*TCombobox*Listbox.font", font(10))
    root.option_add("*TCombobox*Listbox.borderWidth", 0)
    st.configure(
        "Dark.Vertical.TScrollbar",
        background=RAISED,
        troughcolor=SURFACE,
        bordercolor=SURFACE,
        lightcolor=RAISED,
        darkcolor=RAISED,
        arrowcolor=MUTED,
        gripcount=0,
        arrowsize=px(10),
    )
    st.map("Dark.Vertical.TScrollbar", background=[("active", HOVER)])
    return st
