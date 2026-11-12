"Voraesnon drithasaes kudroskou."




import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from . import theme as T
from .theme import px


def round_rect(c, x1, y1, x2, y2, r, **kw):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, splinesteps=16, **kw)


def has_focus(w):
    try:
        return w.focus_get() is w
    except (KeyError, tk.TclError):
        return False


def bg_of(w):
    try:
        return w.cget("bg")
    except tk.TclError:
        return T.BG


class RoundButton(tk.Canvas):
    KINDS = {
        "primary": dict(fill=T.ACCENT, hover=T.ACCENT_HI, press=T.ACCENT_LO, fg=T.ON_ACCENT, outline=""),
        "secondary": dict(fill=T.RAISED, hover=T.HOVER, press=T.BORDER, fg=T.TEXT, outline=T.BORDER),
        "ghost": dict(fill=None, hover=T.RAISED, press=T.HOVER, fg=T.ACCENT, outline=""),
        "danger": dict(fill=T.RAISED, hover="#3a2620", press="#4a2a22", fg=T.ERROR, outline=T.BORDER),
    }

    def __init__(self, parent, text, command=None, kind="primary", width=None, height=36, size=10, stretch=False):
        self.kind = kind
        self.command = command
        self.text = text
        self.enabled = True
        self._state = "normal"
        self._font = T.font(size, "semibold")
        self._fixed_w = width
        self._h = px(height)
        self._stretch = stretch
        self._bg = bg_of(parent)
        super().__init__(parent, height=self._h, width=self._natural_width(), bg=self._bg, highlightthickness=0, bd=0, cursor="hand2", takefocus=1)
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Enter>", lambda e: self._set_state("hover"))
        self.bind("<Leave>", lambda e: self._set_state("normal"))
        self.bind("<ButtonPress-1>", lambda e: self._set_state("press"))
        self.bind("<ButtonRelease-1>", self._release)
        self.bind("<KeyPress-space>", lambda e: self.invoke())
        self.bind("<FocusIn>", lambda e: self._draw())
        self.bind("<FocusOut>", lambda e: self._draw())
        self._draw()

    def _natural_width(self):
        w = tkfont.Font(font=self._font).measure(self.text) + px(34)
        if self._fixed_w:
            w = max(w, px(self._fixed_w))
        return w

    def _set_state(self, s):
        self._state = s
        self._draw()

    def _release(self, e):
        inside = 0 <= e.x <= self.winfo_width() and 0 <= e.y <= self.winfo_height()
        self._set_state("hover" if inside else "normal")
        if inside:
            self.invoke()

    def invoke(self):
        if self.enabled and self.command:
            self.command()

    def configure_button(self, text=None, command=None, kind=None, enabled=None):
        if text is not None:
            self.text = text
            if not self._stretch:
                self.configure(width=self._natural_width())
        if command is not None:
            self.command = command
        if kind is not None:
            self.kind = kind
        if enabled is not None:
            self.enabled = enabled
            self.configure(cursor="hand2" if enabled else "arrow")
        self._draw()

    def _draw(self):
        self.delete("all")
        k = self.KINDS[self.kind]
        w = max(self.winfo_width(), 2) if self.winfo_ismapped() else int(self.cget("width"))
        h = self._h
        fill = k["fill"] or self._bg
        if not self.enabled:
            fill = T.RAISED if self.kind == "primary" else (k["fill"] or self._bg)
            fg = T.DIM
        else:
            fill = {"hover": k["hover"], "press": k["press"]}.get(self._state, fill)
            fg = k["fg"]
        outline = k["outline"] or ""
        if has_focus(self) and self.enabled:
            outline = T.ACCENT_HI if self.kind != "primary" else T.TEXT
        round_rect(self, 1, 1, w - 1, h - 1, px(8), fill=fill, outline=outline, width=1)
        self.create_text(w / 2, h / 2, text=self.text, fill=fg, font=self._font)


class RoundFrame(tk.Frame):
    ""


    def __init__(self, parent, fill=T.SURFACE, outline=T.BORDER, radius=12, pad=16, outline_width=1):
        pbg = bg_of(parent)
        super().__init__(parent, bg=pbg)
        self.fill = fill
        self.outline = outline
        self.outline_width = max(1, px(outline_width))
        self.radius = px(radius)
        self.back = tk.Canvas(self, bg=pbg, highlightthickness=0, bd=0)
        self.back.place(x=0, y=0, relwidth=1, relheight=1)
        self.inner = tk.Frame(self, bg=fill)
        self.inner.pack(fill="both", expand=True, padx=px(pad), pady=px(pad))
        self.back.bind("<Configure>", self._redraw)

    def set_colors(self, fill=None, outline=None):
        if fill:
            self.fill = fill
            self.inner.configure(bg=fill)
        if outline is not None:
            self.outline = outline
        self._redraw()

    def _redraw(self, _e=None):
        c = self.back
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w > 4 and h > 4:
            o = self.outline_width
            round_rect(c, o, o, w - o, h - o, self.radius, fill=self.fill, outline=self.outline, width=o)







HATCH_SAMPLES = 4
HATCH_STRENGTH = 0.42
_HATCH_PNG = {}


def _png_rgba(w, h, rows):
    ""
    import struct
    import zlib

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)

    raw = b"".join(b"\x00" + r for r in rows)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def hatch_tile(spacing, stroke, samples=HATCH_SAMPLES):
    ""

    s, r, n = spacing, stroke / 2.0, samples
    root2 = 2 ** 0.5

    def on(x, y):
        for d in ((x + y) % s, (x - y) % s):
            if min(d, s - d) / root2 <= r:
                return True
        return False

    return [[sum(1 for i in range(n) for j in range(n) if on(tx + (i + 0.5) / n, ty + (j + 0.5) / n)) / float(n * n)
             for tx in range(s)] for ty in range(s)]


def _round_rect_cover(x, y, w, h, radius, samples=HATCH_SAMPLES):
    ""
    n, inside = samples, 0
    for i in range(n):
        for j in range(n):
            sx, sy = x + (i + 0.5) / n, y + (j + 0.5) / n
            cx = radius if sx < radius else (w - radius if sx > w - radius else sx)
            cy = radius if sy < radius else (h - radius if sy > h - radius else sy)
            if (sx - cx) ** 2 + (sy - cy) ** 2 <= radius * radius:
                inside += 1
    return inside / float(n * n)


def hatch_alpha(w, h, spacing, stroke, radius=0, strength=HATCH_STRENGTH):
    ""

    tile = hatch_tile(spacing, stroke)
    rows = []
    for y in range(h):
        trow = tile[y % spacing]
        row = []
        for x in range(w):
            a = trow[x % spacing]
            if radius and a and (x < radius or x >= w - radius) and (y < radius or y >= h - radius):
                a *= _round_rect_cover(x, y, w, h, radius)
            row.append(int(round(255 * strength * a)))
        rows.append(row)
    return rows


def hatch_png(w, h, color, spacing, stroke, radius=0):
    ""
    key = (w, h, color, spacing, round(stroke, 2), radius)
    if key not in _HATCH_PNG:
        rgb = bytes(int(color[i:i + 2], 16) for i in (1, 3, 5))
        rows = [b"".join(rgb + bytes([a]) for a in row) for row in hatch_alpha(w, h, spacing, stroke, radius)]
        _HATCH_PNG[key] = _png_rgba(w, h, rows)
    return _HATCH_PNG[key]


def hatch_image(master, w, h, radius=0, color=None):
    ""
    import base64
    try:
        spacing = max(5, int(round(7 * T._scale)))
        data = base64.b64encode(hatch_png(max(2, int(w)), max(2, int(h)), color or T.ERROR, spacing, max(1.0, 1.1 * T._scale), int(radius)))
        return tk.PhotoImage(master=master, data=data.decode("ascii"), format="png")
    except tk.TclError:
        return None


class Segmented(tk.Canvas):
    ""


    def __init__(self, parent, options, value, command=None, height=36, size=10):
        self._bgc = bg_of(parent)



        from .compact import segmented_request

        f = tkfont.Font(root=parent, font=T.font(size, "semibold"))
        need = segmented_request([f.measure(str(l)) for _, l in options], px(24))
        super().__init__(parent, height=px(height), width=need, bg=self._bgc, highlightthickness=0, bd=0, cursor="hand2")
        self.options = list(options)
        self.value = value
        self.command = command
        self.enabled = True

        self.disabled = set()
        self.on_disabled = None
        self.hatched = set()
        self._hatch = {}
        self._hover = None
        self._font = T.font(size, "semibold")
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Motion>", self._motion)
        self.bind("<Leave>", lambda e: self._set_hover(None))
        self.bind("<Button-1>", self._click)

    def _index_at(self, x):
        w = max(self.winfo_width(), 1)
        return min(len(self.options) - 1, max(0, int(x / (w / len(self.options)))))

    def _motion(self, e):
        self._set_hover(self._index_at(e.x))

    def _set_hover(self, i):
        if i != self._hover:
            self._hover = i
            self._draw()

    def _click(self, e):
        if not self.enabled:
            return
        v = self.options[self._index_at(e.x)][0]
        if v in self.disabled:
            if self.on_disabled:
                self.on_disabled(v)
            return
        if v != self.value:
            self.set(v)
            if self.command:
                self.command(v)

    def set(self, v):
        self.value = v
        self._draw()

    def set_enabled(self, on):
        self.enabled = on
        self.configure(cursor="hand2" if on else "arrow")
        self._draw()

    def set_options(self, options, disabled=()):
        ""
        self.options = list(options)
        self.disabled = set(disabled)
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4:
            return
        round_rect(self, 1, 1, w - 1, h - 1, px(9), fill=T.well_for(self._bgc), outline=T.BORDER)
        n = len(self.options)
        seg = (w - 2) / n
        for i, (v, label) in enumerate(self.options):
            x1 = 1 + i * seg
            sel = v == self.value
            if sel:
                round_rect(self, x1 + px(3), px(3), x1 + seg - px(3), h - px(3), px(7), fill=T.ACCENT if self.enabled else T.BORDER, outline="")
                fg = T.ON_ACCENT if self.enabled else T.MUTED
            else:
                off = not self.enabled or v in self.disabled
                if self._hover == i and not off:
                    round_rect(self, x1 + px(3), px(3), x1 + seg - px(3), h - px(3), px(7), fill=T.HOVER, outline="")
                fg = T.DIM if off else T.TEXT
                if v in self.hatched and v in self.disabled:

                    x0, hw, hh = int(round(x1 + px(3))), int(seg - 2 * px(3)), int(h - 2 * px(3))
                    img = self._hatch.get((hw, hh))
                    if img is None:
                        img = self._hatch[(hw, hh)] = hatch_image(self, hw, hh, radius=px(7))
                    if img is not None:
                        self.create_image(x0, px(3), image=img, anchor="nw", tags=("hatch",))
                        fg = T.MUTED
            self.create_text(x1 + seg / 2, h / 2, text=label, fill=fg, font=self._font)


def folder_tab_spans(width, n, gap):
    ""

    seg = width / float(max(1, n))
    out = []
    for i in range(n):
        x1 = 1 if i == 0 else i * seg + gap / 2.0
        x2 = (i + 1) * seg - (gap / 2.0 if i < n - 1 else 1)
        out.append((x1, x2))
    return out


class FolderTabs(Segmented):
    ""







    def __init__(self, parent, options, value, command=None, height=32, size=10, tab_w=120, gap=4):
        super().__init__(parent, options, value, command=command, height=height, size=size)
        f = tkfont.Font(root=parent, font=T.font(size, "semibold"))
        self._tab_w = max(px(tab_w), max([f.measure(str(l)) for _, l in options] + [0]) + px(40))
        self._gap = px(gap)
        self.on_selected = None
        self.configure(width=self._tab_w * max(1, len(self.options)))

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4:
            return
        r = px(8)
        lift = px(3)
        chosen = None
        for i, ((v, label), (x1, x2)) in enumerate(zip(self.options, folder_tab_spans(w, len(self.options), self._gap))):
            sel = v == self.value
            off = not self.enabled or v in self.disabled
            if sel:
                y1, fill, outline = 1, T.FOLDER, T.FOLDER_EDGE
                fg = T.MUTED if off else T.TEXT
                chosen = (x1, x2)
            else:
                y1, outline = 1 + lift, T.BORDER
                fill = T.HOVER if (self._hover == i and not off) else T.SURFACE
                fg = T.DIM if off else T.MUTED



            round_rect(self, x1, y1, x2, h + r + 2, r, fill=fill, outline=outline, width=1)
            self.create_text((x1 + x2) / 2, (y1 + h) / 2, text=label, fill=fg, font=self._font)
        if self.on_selected:
            self.on_selected(chosen)


class FolderPanel(RoundFrame):
    ""



    def __init__(self, parent, fill=T.FOLDER, outline=T.FOLDER_EDGE, radius=12, pad=10):
        self.gap = None
        super().__init__(parent, fill=fill, outline=outline, radius=radius, pad=pad)

    def set_gap(self, span):
        if span != self.gap:
            self.gap = span
            self._redraw()

    def _redraw(self, _e=None):
        c = self.back
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w <= 4 or h <= 4:
            return
        r = self.radius
        round_rect(c, 1, 1, w - 1, h - 1, r, fill=self.fill, outline=self.outline, width=1)

        c.create_rectangle(1, 1, 1 + r, 1 + r, fill=self.fill, outline="")
        c.create_line(1, 1, 1, 2 + r, fill=self.outline)
        c.create_line(1, 1, 2 + r, 1, fill=self.outline)
        if self.gap:
            x1, x2 = self.gap

            c.create_rectangle(int(round(x1)) + 1, 0, int(round(x2)), 2, fill=self.fill, outline="", tags=("gap",))


class CheckBox(tk.Frame):
    ""

    def __init__(self, parent, text, variable, command=None, size=10, info=None):
        super().__init__(parent, bg=bg_of(parent), cursor="hand2")
        self.var = variable
        self.command = command
        s = px(16)
        self.box = tk.Canvas(self, width=s, height=s, bg=bg_of(parent), highlightthickness=0, bd=0)
        self.box.pack(side="left")
        self.label = tk.Label(self, text=text, bg=bg_of(parent), fg=T.MUTED, font=T.font(size))
        self.label.pack(side="left", padx=(px(7), 0))
        self.info = None
        if info:
            self.info = InfoTip(self, info)
            self.info.pack(side="left", padx=(px(4), 0))
        for w in (self, self.box, self.label):
            w.bind("<Button-1>", self._toggle)
            w.bind("<Enter>", lambda e: self.label.configure(fg=T.TEXT))
            w.bind("<Leave>", lambda e: self.label.configure(fg=T.MUTED))
        self.var.trace_add("write", lambda *a: self._draw())
        self._draw()

    def _toggle(self, _e=None):
        self.var.set(not self.var.get())
        if self.command:
            self.command()

    def _draw(self):
        c = self.box
        c.delete("all")
        s = px(16)
        on = bool(self.var.get())
        round_rect(c, 1, 1, s - 1, s - 1, px(5), fill=T.ACCENT if on else T.RAISED, outline=T.ACCENT if on else "#5a5349")
        if on:
            c.create_line(s * 0.27, s * 0.52, s * 0.44, s * 0.69, s * 0.74, s * 0.33, fill=T.ON_ACCENT, width=max(2, px(2)), capstyle="round", joinstyle="round")


class Field(tk.Frame):
    ""



    def __init__(self, parent, label, variable, placeholder="", secret=False, width=10, compact=False, info=None):
        super().__init__(parent, bg=bg_of(parent))
        self.var = variable
        self.placeholder = placeholder
        self.secret = secret
        self._revealed = False
        self._error = False
        self.buttons = []
        self.info = None
        if label is not None:
            head = tk.Frame(self, bg=bg_of(parent))
            head.pack(fill="x")
            tk.Label(head, text=label, bg=bg_of(parent), fg=T.MUTED, font=T.font(9, "semibold"), anchor="w").pack(side="left")
            if info:
                self.info = InfoTip(head, info)
                self.info.pack(side="left", padx=(px(5), 0))

        self.row = tk.Frame(self, bg=bg_of(parent))
        self.row.pack(fill="x", pady=(px(3) if label is not None else 0, 0))
        well = T.well_for(bg_of(parent))
        self.box = tk.Frame(self.row, bg=well, highlightthickness=1, highlightbackground=T.BORDER, highlightcolor=T.ACCENT)
        self.box.pack(side="left", fill="x", expand=True)
        self.entry = tk.Entry(
            self.box, textvariable=variable, bg=well, fg=T.TEXT, insertbackground=T.ACCENT, relief="flat", bd=0,
            font=T.font(10), width=width, disabledbackground=well if well == T.WELL else T.SURFACE, disabledforeground=T.DIM, selectbackground=T.ACCENT, selectforeground=T.ON_ACCENT,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(px(10), px(6)), pady=px(4 if compact else 5))
        if secret:
            self.eye = tk.Label(self.box, text="Show", bg=well, fg=T.DIM, font=T.font(8, "semibold"), cursor="hand2")
            self.eye.pack(side="right", padx=(0, px(8)))
            self.eye.bind("<Button-1>", self._toggle_reveal)
        self.hint = tk.Label(self.box, text=placeholder, bg=well, fg=T.DIM, font=T.font(10), anchor="w", cursor="xterm")
        self.hint.bind("<Button-1>", lambda e: self.entry.focus_set())
        self.entry.bind("<FocusIn>", lambda e: self._refresh(True))
        self.entry.bind("<FocusOut>", lambda e: self._refresh(False))
        self.var.trace_add("write", lambda *a: self._refresh(has_focus(self.entry)))
        self._apply_secret()
        self.after_idle(lambda: self._refresh(False))

    def _apply_secret(self):
        if self.secret:
            self.entry.configure(show="" if self._revealed else "•")
            self.eye.configure(text="Hide" if self._revealed else "Show")

    def _toggle_reveal(self, _e=None):
        self._revealed = not self._revealed
        self._apply_secret()

    def reveal(self, on=True):
        ""

        self._revealed = bool(on)
        self._apply_secret()

    @property
    def revealed(self):
        ""
        return self._revealed

    def add_button(self, text, command, tip=None):
        ""


        b = RoundButton(self.row, text, command, kind="ghost", height=26, size=9)


        b.pack(side="right", padx=(px(4), 0), before=self.buttons[-1] if self.buttons else self.box)
        self.buttons.append(b)
        if tip:
            Tooltip(b, tip)
        return b

    def set_error(self, on):
        ""
        self._error = bool(on)
        self._refresh(has_focus(self.entry))

    def _refresh(self, focused):
        edge = T.ERROR if self._error else (T.ACCENT if focused else T.BORDER)
        self.box.configure(highlightbackground=edge, highlightcolor=T.ERROR if self._error else T.ACCENT)
        if self.placeholder and not self.var.get() and not focused:
            self.hint.place(in_=self.entry, x=0, rely=0.5, anchor="w")
        else:
            self.hint.place_forget()

    def set_enabled(self, on):
        self.entry.configure(state="normal" if on else "disabled")


class ProgressBar(tk.Canvas):
    def __init__(self, parent, height=8):

        super().__init__(parent, height=px(height), width=px(40), bg=bg_of(parent), highlightthickness=0, bd=0)
        self.frac = 0.0
        self._indet = False
        self._phase = 0.0
        self.bind("<Configure>", lambda e: self._draw())

    def set(self, frac):
        self._indet = False
        self.frac = max(0.0, min(1.0, frac))
        self._draw()

    def indeterminate(self):
        if not self._indet:
            self._indet = True
            self._tick()

    def _tick(self):
        if not self._indet or not self.winfo_exists():
            return
        self._phase = (self._phase + 0.02) % 1.4
        self._draw()
        self.after(30, self._tick)

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4:
            return
        round_rect(self, 0, 0, w, h, h / 2, fill=T.RAISED, outline="")
        if self._indet:
            x1 = (self._phase - 0.4) * w
            x2 = x1 + 0.4 * w
            x1, x2 = max(0, x1), min(w, x2)
            if x2 - x1 > h:
                round_rect(self, x1, 0, x2, h, h / 2, fill=T.ACCENT, outline="")
        elif self.frac > 0:
            round_rect(self, 0, 0, max(h, w * self.frac), h, h / 2, fill=T.ACCENT, outline="")


class Spinner(tk.Canvas):
    def __init__(self, parent, size=16, color=T.ACCENT):
        s = px(size)
        super().__init__(parent, width=s, height=s, bg=bg_of(parent), highlightthickness=0, bd=0)
        self.s = s
        self.color = color
        self._angle = 0
        self._on = False

    def start(self):
        if not self._on:
            self._on = True
            self._tick()

    def stop(self):
        self._on = False
        self.delete("all")

    def _tick(self):
        if not self._on or not self.winfo_exists():
            return
        try:
            hidden = self.winfo_toplevel().state() == "iconic"
        except tk.TclError:
            hidden = False
        if hidden:


            self.after(500, self._tick)
            return
        self.delete("all")
        p = max(2, px(2))
        self.create_oval(p, p, self.s - p, self.s - p, outline=T.BORDER, width=p)
        self.create_arc(p, p, self.s - p, self.s - p, start=self._angle, extent=100, style="arc", outline=self.color, width=p)
        self._angle = (self._angle - 12) % 360
        self.after(30, self._tick)


class Dot(tk.Canvas):
    def __init__(self, parent, color=T.OK, size=10):
        s = px(size)
        super().__init__(parent, width=s, height=s, bg=bg_of(parent), highlightthickness=0, bd=0)
        self.s = s
        self.set(color)

    def set(self, color):
        self.delete("all")
        self.create_oval(1, 1, self.s - 1, self.s - 1, fill=color, outline="")


class EyeToggle(tk.Canvas):
    ""

    def __init__(self, parent, command, size=22, shown=False):
        s = px(size)
        super().__init__(parent, width=s, height=s, bg=bg_of(parent), highlightthickness=0, bd=0, cursor="hand2")
        self.s, self.command, self.shown, self._hover = s, command, shown, False
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self._draw()

    def _set_hover(self, on):
        self._hover = on
        self._draw()

    def _click(self, _e=None):
        self.shown = not self.shown
        self._draw()
        self.command(self.shown)

    def _draw(self):
        self.delete("all")
        s = self.s
        col = T.ACCENT_HI if self._hover else T.ACCENT
        w = max(1, px(1.6))
        m, cy = s * 0.12, s / 2

        self.create_arc(m, cy - s * 0.42, s - m, cy + s * 0.42, start=20, extent=140, style="arc", outline=col, width=w)
        self.create_arc(m, cy - s * 0.42, s - m, cy + s * 0.42, start=200, extent=140, style="arc", outline=col, width=w)
        r = s * 0.13
        self.create_oval(s / 2 - r, cy - r, s / 2 + r, cy + r, fill=col, outline="")
        if not self.shown:
            self.create_line(s * 0.18, s * 0.82, s * 0.82, s * 0.18, fill=col, width=w, capstyle="round")


class CopyIcon(tk.Canvas):
    ""



    def __init__(self, parent, command=None, size=22):
        s = px(size)
        super().__init__(parent, width=s, height=s, bg=bg_of(parent), highlightthickness=0, bd=0, cursor="hand2")
        self.s, self.command, self.text, self.enabled, self._hover = s, command, "Copy", True, False
        self.bind("<Button-1>", lambda e: self.invoke())
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self._draw()

    def _set_hover(self, on):
        self._hover = on
        self._draw()

    def invoke(self):
        if self.enabled and self.command:
            self.command()

    def configure_button(self, text=None, command=None, **_kw):
        if text is not None:
            self.text = text
        if command is not None:
            self.command = command
        self._draw()

    def _draw(self):
        self.delete("all")
        s = self.s
        w = max(1, px(1.6))
        if self.text == "Copied":
            self.create_line(s * 0.2, s * 0.52, s * 0.42, s * 0.74, s * 0.8, s * 0.28, fill=T.OK, width=w * 1.2, capstyle="round", joinstyle="round")
            return
        col = T.ACCENT_HI if self._hover else T.ACCENT

        self.create_line(s * 0.36, s * 0.24, s * 0.36, s * 0.14, s * 0.84, s * 0.14, s * 0.84, s * 0.62, s * 0.74, s * 0.62, fill=col, width=w, capstyle="round", joinstyle="round")
        self.create_rectangle(s * 0.16, s * 0.34, s * 0.64, s * 0.86, outline=col, width=w)


class FolderIcon(tk.Canvas):
    ""


    def __init__(self, parent, command=None, size=18):
        s = px(size)
        super().__init__(parent, width=s, height=s, bg=bg_of(parent), highlightthickness=0, bd=0, cursor="hand2")
        self.s, self.command, self.enabled, self._hover = s, command, True, False
        self.bind("<Button-1>", lambda e: self.invoke())
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self._draw()

    def _set_hover(self, on):
        self._hover = on
        self._draw()

    def invoke(self):
        if self.enabled and self.command:
            self.command()

    def set(self, command=None, enabled=None):
        if command is not None:
            self.command = command
        if enabled is not None:
            self.enabled = bool(enabled)
            self.configure(cursor="hand2" if self.enabled else "arrow")
        self._draw()

    def _draw(self):
        self.delete("all")
        s = self.s
        w = max(1, px(1.5))
        col = T.DIM if not self.enabled else (T.ACCENT_HI if self._hover else T.ACCENT)

        self.create_line(s * 0.12, s * 0.34, s * 0.12, s * 0.2, s * 0.4, s * 0.2, s * 0.5, s * 0.32, s * 0.88, s * 0.32,
                         fill=col, width=w, capstyle="round", joinstyle="round")
        self.create_rectangle(s * 0.12, s * 0.34, s * 0.88, s * 0.82, outline=col, width=w)


class Banner(tk.Frame):
    ""

    COLORS = {"error": (T.ERROR, T.ERROR_BG, T.TEXT), "info": (T.ACCENT, T.INFO_BG, T.TEXT), "ok": (T.OK, T.INFO_BG, T.TEXT)}

    def __init__(self, parent, wrap=380):
        super().__init__(parent, bg=bg_of(parent))
        self.bar = tk.Frame(self, width=px(3), bg=T.ERROR)
        self.bar.pack(side="left", fill="y")
        self.label = tk.Label(self, text="", bg=T.ERROR_BG, fg=T.TEXT, font=T.font(9), justify="left", anchor="w", wraplength=px(wrap), padx=px(10), pady=px(8))
        self.label.pack(side="left", fill="both", expand=True)
        self._shown = False

    def show(self, text, kind="error"):
        edge, bg, fg = self.COLORS.get(kind, self.COLORS["info"])
        self.bar.configure(bg=edge)
        self.label.configure(text=text, bg=bg, fg=fg)
        self._shown = True

    def hide(self):
        self.label.configure(text="")
        self._shown = False


class ScrollArea(tk.Frame):
    ""




    def __init__(self, parent, gutter=12, on_change=None):
        bg = bg_of(parent)
        super().__init__(parent, bg=bg)
        self.on_change = on_change
        self._last_h = None
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, width=1, height=1, yscrollincrement=px(24))
        self.gutter = tk.Frame(self, bg=bg, width=px(gutter))
        self.gutter.pack(side="right", fill="y")
        self.gutter.pack_propagate(False)
        self.bar = ttk.Scrollbar(self.gutter, orient="vertical", style="Dark.Vertical.TScrollbar", command=self.canvas.yview)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.bar.set)
        self.body = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window(0, 0, window=self.body, anchor="nw")
        self.scrolls = False
        self.body.bind("<Configure>", lambda e: self._sync())
        self.canvas.bind("<Configure>", self._on_canvas)
        self.bind_all("<MouseWheel>", self._on_wheel, add="+")

    def _sync(self):
        rh = self.body.winfo_reqheight()
        self.canvas.configure(scrollregion=(0, 0, self.canvas.winfo_width(), rh), height=rh)


        ch = self.canvas.winfo_height()
        self.canvas.itemconfigure(self._win, height=max(rh, ch) if ch > 1 else rh)
        self._update_bar()
        if rh != self._last_h:
            self._last_h = rh
            if self.on_change:
                self.after_idle(self.on_change)

    def _on_canvas(self, e):
        self.canvas.itemconfigure(self._win, width=e.width)
        self._sync()

    def _update_bar(self):
        need = self.body.winfo_reqheight() > self.canvas.winfo_height() + 1 and self.canvas.winfo_height() > 1
        if need != self.scrolls:
            self.scrolls = need
            if need:
                self.bar.pack(fill="y", expand=True)
            else:
                self.bar.pack_forget()
                self.canvas.yview_moveto(0)

    def _on_wheel(self, e):
        if not self.scrolls:
            return
        w = e.widget
        if not isinstance(w, tk.Misc) or isinstance(w, tk.Listbox) or not str(w).startswith(str(self)):
            return
        self.canvas.yview_scroll(int(-e.delta / 120) or (-1 if e.delta > 0 else 1), "units")

    def see(self, widget):
        ""
        if not self.scrolls:
            return
        try:
            y = widget.winfo_rooty() - self.body.winfo_rooty()
            h = widget.winfo_height()
            top = self.canvas.canvasy(0)
            ch = self.canvas.winfo_height()
            total = max(1, self.body.winfo_reqheight())
            if y < top:
                self.canvas.yview_moveto(y / total)
            elif y + h > top + ch:
                self.canvas.yview_moveto((y + h - ch) / total)
        except tk.TclError:
            pass


TIP_DELAY_MS = 300
TIP_WRAP = 380


def _tip_work_area(widget):
    ""
    try:
        return T.work_area(T.window_handle(widget.winfo_toplevel()))
    except Exception:
        try:
            return (0, 0, widget.winfo_screenwidth(), widget.winfo_screenheight())
        except tk.TclError:
            return (0, 0, 1280, 680)


_OPEN_TIPS = set()


def hide_all_tips(_e=None):
    ""

    for p in list(_OPEN_TIPS):
        p.hide()


class _TipPopup:
    ""


    def __init__(self, widget):
        self.widget = widget
        self.win = None

    @property
    def shown(self):
        return self.win is not None

    def show(self, text, at=None, still=None):
        ""


        if not text or self.win is not None:
            return
        from .compact import cursor_tip_position, tip_parts, tip_position

        w = self.widget
        try:
            if not w.winfo_viewable():
                return
            win = tk.Toplevel(w)
        except tk.TclError:
            return
        self.win = win
        _OPEN_TIPS.add(self)
        win.withdraw()
        win.wm_overrideredirect(True)
        win.configure(bg=T.BORDER)
        headline, body = tip_parts(text)
        box = tk.Frame(win, bg=T.RAISED, padx=px(9), pady=px(6))
        box.pack(padx=1, pady=1)
        if headline:

            tk.Label(box, text=headline, bg=T.RAISED, fg=T.TEXT, font=T.font(9, "bold"), justify="left",
                     wraplength=px(TIP_WRAP), padx=0, pady=0).pack(anchor="w", pady=(0, px(6)))
        if body:
            tk.Label(box, text=body, bg=T.RAISED, fg=T.TEXT, font=T.font(9), justify="left",
                     wraplength=px(TIP_WRAP), padx=0, pady=0).pack(anchor="w")
        try:
            win.update_idletasks()
            size = (win.winfo_reqwidth(), win.winfo_reqheight())
            if at is not None:
                x, y = cursor_tip_position(at, size, _tip_work_area(w))
                if still is not None:
                    def follow(e):
                        if not still(e.x_root, e.y_root):
                            self.hide()
                    win.bind("<Motion>", follow)
                    win.bind("<Leave>", follow)
                    win.bind("<ButtonPress>", lambda e: self.hide())
            else:
                anchor = (w.winfo_rootx(), w.winfo_rooty(), w.winfo_width(), w.winfo_height())
                x, y = tip_position(anchor, size, _tip_work_area(w), gap=px(4))
            self.pos = (x, y)
            win.wm_geometry("+%d+%d" % (x, y))
            win.deiconify()
            win.lift()
        except tk.TclError:
            self.hide()

    def hide(self):
        _OPEN_TIPS.discard(self)
        if self.win is not None:
            try:
                self.win.destroy()
            except tk.TclError:
                pass
            self.win = None


class Tooltip:
    ""




    def __init__(self, widget, text_fn, at_cursor=False):
        self.widget = widget
        self.text_fn = text_fn
        self.at_cursor = at_cursor
        self.popup = _TipPopup(widget)
        self._job = None
        self._shown_text = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._leave if at_cursor else self._hide, add="+")
        if at_cursor:
            widget.bind("<Motion>", self._moved, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")
        widget.bind("<Unmap>", self._hide, add="+")
        widget.bind("<Destroy>", self._hide, add="+")

    @property
    def tip(self):
        return self.popup.win

    def _text(self):
        return self.text_fn() if callable(self.text_fn) else self.text_fn

    def _schedule(self, _e=None):
        self._cancel()
        try:
            self._job = self.widget.after(TIP_DELAY_MS, self._show)
        except tk.TclError:
            self._job = None

    def _cancel(self):
        if self._job is not None:
            try:
                self.widget.after_cancel(self._job)
            except tk.TclError:
                pass
            self._job = None

    def _show(self, _e=None):
        self._job = None
        text = self._text()
        if not self.at_cursor:
            self.popup.show(text)
            return
        try:
            at = self.widget.winfo_pointerxy()
        except tk.TclError:
            return
        self._shown_text = text
        self.popup.show(text, at=at, still=self._still)

    def _hide(self, _e=None):
        self._cancel()
        self.popup.hide()

    def _over(self, x, y):
        ""
        w = self.widget
        try:
            wx, wy = w.winfo_rootx(), w.winfo_rooty()
            return wx <= x < wx + w.winfo_width() and wy <= y < wy + w.winfo_height()
        except tk.TclError:
            return False

    def _still(self, x, y):
        ""
        return self._over(x, y) and self._text_at(x, y) == self._shown_text

    def _text_at(self, x, y):
        f = getattr(self.text_fn, "at", None)
        return f(x - self.widget.winfo_rootx(), y - self.widget.winfo_rooty()) if f else self._text()

    def _leave(self, e=None):
        ""
        try:
            x, y = self.widget.winfo_pointerxy()
        except tk.TclError:
            x = y = None
        if x is None or not self._over(x, y):
            self._hide()

    def _moved(self, _e=None):
        ""

        if self.popup.shown and self._text() != self._shown_text:
            self.popup.hide()
        if not self.popup.shown:
            self._schedule()


INFO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "info")
INFO_MIN, INFO_MAX = 10, 40


def _info_images(master, n, info_dir=INFO_DIR):
    ""

    n = max(INFO_MIN, min(INFO_MAX, int(round(n))))
    try:
        idle = os.path.join(info_dir, "info-%d-idle.png" % n)
        lit = os.path.join(info_dir, "info-%d-lit.png" % n)
        if not (os.path.isfile(idle) and os.path.isfile(lit)):
            return None
        return (tk.PhotoImage(master=master, file=idle), tk.PhotoImage(master=master, file=lit))
    except (tk.TclError, OSError):
        return None


class InfoTip(tk.Canvas):
    ""




    def __init__(self, parent, text, size=14):
        self._bgc = bg_of(parent)
        self.s = px(size)
        pad = max(2, px(2))
        super().__init__(parent, width=self.s + 2 * pad, height=self.s + 2 * pad, bg=self._bgc, highlightthickness=0, bd=0,
                         cursor="hand2", takefocus=1)
        self.pad = pad
        self.text = text


        self._imgs = _info_images(self, self.s)
        self.popup = _TipPopup(self)
        self._hover = False
        self._job = None
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<Button-1>", self._click)
        self.bind("<FocusIn>", self._focus_in)
        self.bind("<FocusOut>", self._focus_out)
        self.bind("<KeyPress-Return>", self._key_toggle)
        self.bind("<KeyPress-space>", self._key_toggle)
        self.bind("<KeyPress-Escape>", self._key_hide)
        self.bind("<Unmap>", lambda e: self.hide())
        self.bind("<Destroy>", lambda e: self.hide())
        self._draw()

    def current_text(self):
        try:
            return self.text() if callable(self.text) else self.text
        except Exception:
            return None

    def show(self):
        self._cancel()
        self.popup.show(self.current_text())

    def hide(self):
        self._cancel()
        self.popup.hide()

    def toggle(self):
        if self.popup.shown:
            self.hide()
        else:
            self.show()

    def _cancel(self):
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except tk.TclError:
                pass
            self._job = None

    def _enter(self, _e=None):
        self._hover = True
        self._draw()
        self._cancel()
        if not self.popup.shown:
            self._job = self.after(TIP_DELAY_MS, self.show)

    def _leave(self, _e=None):
        self._hover = False
        self._draw()
        if not has_focus(self):
            self.hide()

    def _click(self, _e=None):
        self.toggle()
        return "break"

    def _focus_in(self, _e=None):
        self._draw()
        self.show()

    def _focus_out(self, _e=None):
        self._draw()
        self.hide()

    def _key_toggle(self, _e=None):
        self.toggle()
        return "break"

    def _key_hide(self, _e=None):
        self.hide()
        return "break"

    def _draw(self):
        self.delete("all")
        p, s = self.pad, self.s
        focused = has_focus(self)
        lit = self._hover or focused
        if self._imgs is not None:
            self.create_image(p + s / 2, p + s / 2, image=self._imgs[1 if lit else 0], anchor="center")
            if focused:
                self.create_oval(1, 1, s + 2 * p - 1, s + 2 * p - 1, outline=T.ACCENT_HI, width=1)
            return
        ring = T.ACCENT if lit else T.DIM
        fill = T.RAISED if lit else self._bgc
        self.create_oval(p, p, p + s, p + s, outline=ring, fill=fill, width=max(1, px(1.2)))
        if focused:
            self.create_oval(1, 1, s + 2 * p - 1, s + 2 * p - 1, outline=T.ACCENT_HI, width=1)


        col = T.ACCENT if lit else T.MUTED
        cx = p + s / 2
        sw = max(1.5, s * 0.13)
        dot_r = sw * 0.62
        dot_cy = p + s * 0.31
        self.create_oval(cx - dot_r, dot_cy - dot_r, cx + dot_r, dot_cy + dot_r, fill=col, outline="")
        self.create_line(cx, p + s * 0.45, cx, p + s * 0.75, fill=col, width=sw, capstyle="round")


DISCORD_BLURPLE = "#5865F2"
DISCORD_MUTED = "#6a72b8"
DISCORD_HI = "#7b86ff"



_DISCORD_FACE = [
    (0.27, 0.02), (0.27, 0.02), (0.36, 0.10), (0.50, 0.08), (0.64, 0.10), (0.73, 0.02), (0.73, 0.02),
    (0.87, 0.10), (0.96, 0.40), (1.00, 0.80), (0.86, 0.93), (0.75, 1.00), (0.75, 1.00), (0.69, 0.87),
    (0.50, 0.91), (0.31, 0.87), (0.25, 1.00), (0.25, 1.00), (0.14, 0.93), (0.00, 0.80), (0.04, 0.40),
    (0.13, 0.10),
]


def draw_discord(c, x, y, w, color, bg):
    ""

    h = w * 0.76
    pts = []
    for fx, fy in _DISCORD_FACE:
        pts += [x + fx * w, y + fy * h]
    c.create_polygon(pts, smooth=True, splinesteps=12, fill=color, outline="")
    for ex in (0.36, 0.64):
        rx, ry = w * 0.095, h * 0.13
        cx, cy = x + ex * w, y + 0.56 * h
        c.create_oval(cx - rx, cy - ry, cx + rx, cy + ry, fill=bg, outline="")




ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
ICON_SIZES = (16, 20, 24, 28, 32, 40)
ICON_FILES = {"discord": "discord", "bug": "bug", "github": "github"}


ICON_ROW_H = {16: 22, 20: 28, 24: 34, 28: 39, 32: 45, 40: 56}


def icon_size_for(target, sizes=ICON_SIZES):
    ""
    return min(sizes, key=lambda n: (abs(n - target), n))


def icon_path(glyph, target, assets=ASSETS_DIR):
    ""
    base = ICON_FILES.get(glyph)
    if not base:
        return None
    p = os.path.join(assets, "%s-%d.png" % (base, icon_size_for(target)))
    return p if os.path.isfile(p) else None


def icon_image(master, glyph, target):
    ""

    p = icon_path(glyph, target)
    if p is None:
        return None
    try:
        return tk.PhotoImage(master=master, file=p)
    except (tk.TclError, OSError):
        return None


def footer_row_h(discord_target):
    ""

    return ICON_ROW_H[icon_size_for(discord_target)]


class IconLink(tk.Canvas):
    ""





    def __init__(self, parent, glyph, command, tip, text=None, size=16, colors=(T.DIM, T.ACCENT), row_h=None):
        self._bgc = bg_of(parent)
        self.glyph, self.command, self.text = glyph, command, text
        self.s = px(size)
        self.colors = colors
        self._font = T.font(9)
        self._gap = px(5)
        tw = tkfont.Font(root=parent, font=self._font).measure(text) if text else 0
        self.pad = max(3, px(3))

        self.row_h = row_h

        self.img = icon_image(parent, glyph, self.s)
        self.iw = self.img.width() if self.img is not None else self.s
        self.logo_h = self.img.height() if self.img is not None else self.s
        width = self.iw + 2 * self.pad + ((self._gap + tw) if text else 0)
        inner = row_h if row_h else self.s
        super().__init__(parent, width=width, height=inner + 2 * self.pad, bg=self._bgc, highlightthickness=0, bd=0,
                         cursor="hand2", takefocus=1)
        self.tip = tip
        self.popup = _TipPopup(self)
        self._hover = False
        self._job = None
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<Button-1>", self._click)
        self.bind("<FocusIn>", lambda e: (self._draw(), self._show()))
        self.bind("<FocusOut>", lambda e: (self._draw(), self._hide()))
        self.bind("<KeyPress-Return>", self._key)
        self.bind("<KeyPress-space>", self._key)
        self.bind("<Destroy>", lambda e: self._hide())
        self._draw()

    def _show(self):
        self._cancel()
        self.popup.show(self.tip() if callable(self.tip) else self.tip)

    def _hide(self):
        self._cancel()
        self.popup.hide()

    def _cancel(self):
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except tk.TclError:
                pass
            self._job = None

    def _enter(self, _e=None):
        self._hover = True
        self._draw()
        self._cancel()
        self._job = self.after(TIP_DELAY_MS, self._show)

    def _leave(self, _e=None):
        self._hover = False
        self._draw()
        if not has_focus(self):
            self._hide()

    def _click(self, _e=None):
        self._hide()
        if self.command:
            self.command()
        return "break"

    def _key(self, _e=None):
        if self.command:
            self.command()
        return "break"

    def _draw(self):
        self.delete("all")
        lit = self._hover or has_focus(self)
        color = self.colors[1] if lit else self.colors[0]
        p, s = self.pad, self.s
        inner = self.row_h if self.row_h else s
        if self.img is not None:


            if self.row_h:

                self.create_image(p, p + inner, image=self.img, anchor="sw")
            else:
                self.create_image(p, p + s / 2, image=self.img, anchor="w")
        elif self.glyph == "discord":
            gh = s * 0.76
            draw_discord(self, p, p + (inner - gh), s, color, self._bgc)
        elif self.glyph == "github":

            x0, y0 = p, p + (inner - s)
            self.create_oval(x0 + s * 0.12, y0 + s * 0.12, x0 + s * 0.88, y0 + s * 0.88, outline=color, width=max(1, px(1.5)))
        elif self.glyph == "bug":

            x0, y0 = p, p + (inner - s)
            self.create_oval(x0 + s * 0.28, y0 + s * 0.30, x0 + s * 0.72, y0 + s * 0.95, outline=color, width=max(1, px(1.5)))
            self.create_oval(x0 + s * 0.38, y0 + s * 0.08, x0 + s * 0.62, y0 + s * 0.32, outline=color, width=max(1, px(1.5)))
            for k in (0.45, 0.62, 0.80):
                self.create_line(x0 + s * 0.08, y0 + s * k, x0 + s * 0.28, y0 + s * k, fill=color, width=max(1, px(1)))
                self.create_line(x0 + s * 0.72, y0 + s * k, x0 + s * 0.92, y0 + s * k, fill=color, width=max(1, px(1)))
        if self.text:

            ty = (p + inner - self.logo_h / 2) if self.row_h else (p + s / 2)
            self.create_text(p + self.iw + self._gap, ty, text=self.text, anchor="w", fill=T.ACCENT if lit else T.DIM, font=self._font)
        if has_focus(self):
            w = int(self.cget("width"))
            round_rect(self, 0.5, 0.5, w - 0.5, inner + 2 * p - 0.5, px(4), fill="", outline=T.ACCENT_HI)


def body_title(body):
    ""

    name = body.get("name") or "Body"
    bg = (body.get("background") or "").strip()
    return "%s — %s" % (name, bg) if bg else name


class BodyRow(tk.Canvas):
    ""

    def __init__(self, parent, body, on_select, on_activate, last_used=False):
        self._bgc = bg_of(parent)
        super().__init__(parent, height=px(58), bg=self._bgc, highlightthickness=0, bd=0)
        self.body = body
        self.free = bool(body.get("free"))
        self.last_used = last_used
        self.selected = False
        self._hover = False
        self.on_select = on_select
        self.configure(cursor="hand2" if self.free else "arrow")
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<Button-1>", lambda e: self.free and on_select(self))
        self.bind("<Double-Button-1>", lambda e: self.free and on_activate(self))

    def _set_hover(self, h):
        self._hover = h
        self._draw()

    def set_selected(self, s):
        self.selected = s
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10:
            return
        if not self.free:
            fill, outline = T.SURFACE, T.BORDER
        elif self.selected:
            fill, outline = "#2d2718", T.ACCENT
        elif self._hover:
            fill, outline = T.HOVER, "#4a443c"
        else:
            fill, outline = T.RAISED, T.BORDER
        round_rect(self, 1, 1, w - 1, h - 1, px(9), fill=fill, outline=outline, width=2 if self.selected else 1)

        cx, cy, r = px(22), h / 2, px(7)
        if self.free:
            self.create_oval(cx - r, cy - r, cx + r, cy + r, outline=T.ACCENT if self.selected else "#5a5349", width=2)
            if self.selected:
                self.create_oval(cx - r / 2, cy - r / 2, cx + r / 2, cy + r / 2, fill=T.ACCENT, outline="")
        name_fg = T.TEXT if self.free else T.DIM
        title = body_title(self.body)
        self.create_text(px(40), h / 2 - px(9), text=title, anchor="w", fill=name_fg, font=T.font(11, "semibold"))
        state = self.body.get("state", "")
        hexid = self.body.get("id_hex", "")
        sub = "%s  ·  %s" % (state, hexid) if state and hexid else (state or hexid)
        self.create_text(px(40), h / 2 + px(10), text=sub, anchor="w", fill=T.MUTED if self.free else T.DIM, font=T.font(9))
        if not self.free:
            tag = "In use by %s" % (self.body.get("held_by") or "someone")
            self.create_text(w - px(14), h / 2, text=tag, anchor="e", fill=T.MUTED, font=T.font(9, "semibold"))
        elif self.last_used:
            f = T.font(8, "semibold")
            tw = tkfont.Font(font=f).measure("LAST USED")
            x2 = w - px(12)
            x1 = x2 - tw - px(16)



            round_rect(self, x1, h / 2 - px(10), x2, h / 2 + px(10), px(4), fill=fill, outline=T.ACCENT)
            self.create_text((x1 + x2) / 2, h / 2, text="LAST USED", fill=T.ACCENT, font=f)
