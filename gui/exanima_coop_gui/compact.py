""











from . import bugreport as BR
from . import directview as DV
from . import steamview as SV



GAP = 8
CARD_PAD = 12
SEG_H = 32
BUTTON_H = 36






PAD_L, PAD_R, GUTTER = 20, 8, 12
LEFT_W = 372
PANEL_W = 321
COL_GAP = 12
WIDE_W = PAD_L + LEFT_W + COL_GAP + PANEL_W + PAD_R + GUTTER
WIDE_H = 451

GATE_WRAP = 255
INST_WRAP = 240


def content_width(win_w, scale):
    ""
    return px_at(win_w, scale) - px_at(PAD_L, scale) - px_at(PAD_R, scale) - px_at(GUTTER, scale)







FOLDER_PAD = 12
SECTION_GAP = 20
TOP_TAB_W = 120
SUB_TABS_W = 280


def section_col_w(wide, narrow_w):
    ""


    if wide:
        inner = WIDE_W - PAD_L - PAD_R - GUTTER - 2 - 2 * FOLDER_PAD
        return (inner - SECTION_GAP) // 2
    return narrow_w - PAD_L - PAD_R - GUTTER - 2 - 2 * FOLDER_PAD


def form_wrap(wide, narrow_w):
    ""
    return section_col_w(wide, narrow_w) - 8


def panel_wrap(wide, narrow_w):
    ""
    return section_col_w(wide, narrow_w) - 6


def advanced_shown(debug_tools):
    ""



    return bool(debug_tools)




NAME_HOST_TIP = "Your player name in the session (friends see it with your ping). Up to 15 letters, digits, spaces or - _ . '"
NAME_JOIN_TIP = ("Your player name in the session: no one else in the game may use it, and the character creator starts with it. "
                 "Up to 15 letters, digits, spaces or - _ . '")
HOST_PW_TIP = "Friends type this to join. Type your own, or press Generate for a random one that is easy to read out."
HOST_PW_NEEDED = "Hosting needs a password: type one or press Generate."



PLAYERS_TIP = ("How many can play at once, you included. A new game starts with you alone. Friends make their own "
               "characters in the game with CREATE on their main menu. New characters can join only when you start a new game.")


def players_summary(n):
    ""
    return "solo" if n == 1 else "you + up to %d friend%s" % (n - 1, "" if n == 2 else "s")



JOIN_NOTE_DIRECT = ("The host starts the game first (Host). You then pick your character from the host's list (its save is downloaded), "
                    "or New character: the game starts at its main menu and CREATE makes your character. "
                    "New characters can join only when the host starts a new game. "
                    "Use your own name each time: the host remembers which character is yours.")
JOIN_NOTE_STEAM = ("The host starts the game first (Host). Your game then starts at its main menu and joins the host there: "
                   "CREATE makes a new character, POSSESS plays your own. New characters can join only when the host starts a new game. "
                   "Use your own name each time: the host remembers which character is yours.")

CODE_TIP = ("The code the host's launcher shows (also in the host's game, under the F1 panel). It looks like ABCD-1234. "
            + SV.FRIENDS_HINT)


ADDR_NOTE = "Give a friend one of these: the Public IP over the internet, a LAN IP at home."


FIREWALL_NOTE = ("Windows may ask to allow Exanima through the firewall: choose Allow (at least Private networks). "
                 "If it was blocked: Windows Security > Firewall & network protection > Allow an app through firewall, "
                 "then tick Exanima.")
ROUTER_HOW = ("The launcher asks your own router (nothing else, and nothing is changed on it) for its internet "
              "address. It cannot see whether friends get through: only a friend joining shows that.")
IPV6_TIP = ("Friends whose internet has IPv6 can join with this address. Many routers block incoming IPv6: "
            "allow UDP port 27500 to this PC in your router's IPv6 settings.")
STEAM_CODE_LATER = "appears once your game runs"


INSTALL_TIP = "Adds the mod to this game folder. Your game itself stays as it is."
UPDATE_TIP = "Updates the mod in this game folder to this download's version. Your game itself stays as it is."
UNINSTALL_TIP = "Removes the mod's files from this game folder. Your game itself stays as it is."


def install_button_tip(label):
    ""
    return {"Install": INSTALL_TIP, "Update": UPDATE_TIP, "Uninstall": UNINSTALL_TIP}.get((label or "").strip())



REMEMBER_TIP = "Stores the password in %APPDATA%\\ExanimaCoop\\launcher.json, encrypted for your Windows user."


def remember_tick_shown(manual):
    ""


    return bool(manual)


def footer_checks_anchor(remember_shown, grid):
    ""

    return "nw" if grid and not remember_shown else "w"


CONSOLE_TIP = "Opens the co-op mod's log window next to the game."
DETAILED_TIP = ("Writes a much more detailed co-op log while you play, for reporting a bug (no cheats, no debug keys; the game runs the same). "
                "The log is exanima-coop.log in %APPDATA%\\ExanimaCoop\\HostSaves\\Exanima when you host, and in %APPDATA%\\ExanimaCoop\\ClientSaves\\Exanima when you join "
                "(a second copy on this PC: HostSaves-instance2 / ClientSaves-instance2, and so on); "
                "physics reports, saved when an object jumps or flies off, are in the coop-physics-reports folder next to it. "
                "Takes effect the next time the game starts.")


TILE_TIP = ("For showing several copies of the game on one screen: each game window fills a quarter of the main "
            "screen (host top-left, then top-right, bottom-left, bottom-right). Extra local copies start windowed; "
            "your own game settings are not changed.")
LOCAL_COPY_NOTE = "Joining a host on this PC (127.0.0.1) uses the next free local copy (up to 3 besides the host)."
TILE_INFO = TILE_TIP + "\n\n" + LOCAL_COPY_NOTE


DISCORD_LABEL = "Veliathon Tinkers"
DISCORD_URL = "https://discord.gg/wDxgGsUmxJ"


DISCORD_TIP = ("Veliathon Tinkers on Discord: news, questions in #help, ideas in #i-would-like, bugs in #bug-reports. "
               "New to the server? Accept the rules in #rules first. Opens in your browser.")


GITHUB_URL = "https://github.com/Veliathon/UnofficialExanimaMPMod"
GITHUB_TIP = "Opens the mod's GitHub page in your browser."



def tip_parts(text):
    ""
    if isinstance(text, tuple) and len(text) == 2:
        return (text[0] or None), (text[1] or "")
    return None, text




BUGREPORT_URL = ""


def bugreport_targets(f):
    ""
    out = []
    gh = BR.issue_form_url(GITHUB_URL, f)
    if gh:
        out.append((BR.GITHUB_LABEL, gh))
    dc = BUGREPORT_URL or DISCORD_URL
    if dc:
        out.append((BR.DISCORD_LABEL, dc))
    return out




REPORT_ICON_TIP = "Report a bug (GitHub or Discord)"


def access_info(access):
    ""

    return "%s\n\nNow: %s\n\n%s" % (SV.ACCESS_TIP, SV.access_note(access), SV.FRIENDS_HINT)



HOST_UPLOAD_NOTE = "The host sends the game to everyone: the player with the best upload should host."


def route_panel(manual, host):
    ""

    if manual and host:
        return DV.MANUAL_HOST_TITLE, ADDR_NOTE + "\n\n" + FIREWALL_NOTE
    if manual:
        return DV.MANUAL_JOIN_TITLE, DV.MANUAL_JOIN_TEXT + "\n\n" + JOIN_NOTE_DIRECT
    if host:
        return SV.STEAM_HOST_TITLE, SV.STEAM_HOST_TEXT + "\n\n" + HOST_UPLOAD_NOTE
    return SV.STEAM_JOIN_TITLE, SV.STEAM_JOIN_TEXT + "\n\n" + JOIN_NOTE_STEAM




ROUTER_SHORT = {
    "ok": "Router OK: it has a public address.",
    "unknown": "Router: couldn't check automatically.",
}


def router_line(kind, text):
    ""
    info = ("%s\n\n%s" % (text, ROUTER_HOW)) if text and kind != "checking" else ROUTER_HOW
    return ROUTER_SHORT.get(kind, text), info


def forward_info(gateway=None):
    ""
    return DV.forward_steps(gateway)




def tip_position(anchor, size, work, gap=4):
    ""



    ax, ay, aw, ah = anchor
    tw, th = size
    left, top, right, bottom = work
    x = max(left, min(ax, right - tw))
    y = ay + ah + gap
    if y + th > bottom:
        above = ay - gap - th
        y = above if above >= top else max(top, bottom - th)
    return x, max(top, y)


def whatsnew_lines(work_h, line_px, chrome_px, most=22, least=6):
    ""

    return max(least, min(most, int((work_h - chrome_px) // max(1, line_px))))


def cursor_tip_position(pointer, size, work):
    ""


    px_, py_ = pointer
    tw, th = size
    left, top, right, bottom = work
    x = max(left, min(px_ - tw // 2, right - tw))
    y = max(top, min(py_ - th // 2, bottom - th))
    return x, y




def flow_rows(widths, avail, gap):
    ""


    rows, cur, used = [], [], 0
    for i, w in enumerate(widths):
        need = w if not cur else used + gap + w
        if cur and need > avail:
            rows.append(cur)
            cur, need = [], w
        cur.append(i)
        used = need
    if cur:
        rows.append(cur)
    return rows


def elide_path(path, fits):
    ""




    if not path or fits(path):
        return path or ""
    sep = "\\" if "\\" in path else "/"
    parts = [p for p in path.rstrip(sep).split(sep) if p]
    head = parts[0] + sep if len(parts) > 1 and parts[0].endswith(":") else ""
    rest = parts[1:] if head else parts
    tries = [head + "…" + sep + sep.join(rest[-k:]) for k in range(len(rest) - 1, 0, -1)] if head else []
    tries += ["…" + sep + sep.join(rest[-k:]) for k in range(len(rest) - 1, 0, -1)]
    for t in tries:
        if fits(t):
            return t
    last = "…" + sep + (rest[-1] if rest else path)
    while len(last) > 2 and not fits(last):
        last = last[:-2] + "…"
    return last


def route_placement(wide):
    ""


    return "beside" if wide else "below"


def footer_checks(wide):
    ""

    return "grid" if wide else "rows"


def px_at(n, scale):
    ""
    return int(round(n * scale))


def segmented_request(label_widths, pad):
    ""


    return (max(list(label_widths) + [0]) + pad) * max(1, len(label_widths))


def columns_fit(scale, win_w, left_min, right_w, pad_left=PAD_L, pad_right=PAD_R, gutter=GUTTER):
    ""


    content = px_at(win_w, scale) - px_at(pad_left, scale) - px_at(pad_right, scale) - px_at(gutter, scale)
    return px_at(left_min, scale) + px_at(right_w, scale) <= content






LINE_8, LINE_9, LINE_10, TITLE_18 = 16, 17, 19, 31
ICON_H = 18
ENTRY_H = LINE_10 + 2 * 5 + 2
ADDR_ROW_H = 26 + 3
CHECK_H = max(16, LINE_9, ICON_H)
FOOTER_ICON_H = 32


def field_h(info=False):
    ""
    return max(LINE_9, ICON_H if info else 0) + 3 + ENTRY_H


def form_height(mode, route, lan_rows=1, router_lines=2, pw_note=True, links_rows=1, advanced_open=False,
                gate_sub_lines=2, open_port_lines=2):
    ""





    top = 2 * 12 + TITLE_18 + GAP
    gate = 2 * 10 + LINE_10 + 1 + gate_sub_lines * LINE_8

    manual = route == "manual"
    if mode == "host":
        form = (field_h(True) + ((GAP + field_h(True) + ((4 + LINE_8) if pw_note else 0)) if manual else 0)
                + (GAP + 2) + ICON_H + 3 + (SEG_H - 2))
    else:
        form = field_h(True) + ((GAP + field_h(False)) if manual else 0)


    if mode == "host" and manual:
        part = ((1 + lan_rows) * ADDR_ROW_H + 4 + 1 + 7 + router_lines * LINE_9 + 1 + LINE_8 + 7
                + max(CHECK_H, open_port_lines * LINE_9) + 5 + max(LINE_8, ICON_H))
    elif mode == "host":
        part = ICON_H + 3 + (SEG_H - 2) + (GAP + 2) + LINE_9
    else:
        part = field_h(route == "steam")

    folder = SEG_H + 2 + 2 * FOLDER_PAD + SEG_H + (GAP + 2) + max(form, part)
    links = (GAP + 2) + links_rows * (max(LINE_9, ICON_H, FOOTER_ICON_H) + 3)
    if advanced_open:
        links += 6 + CHECK_H
    footer = (GAP + 2) + max(BUTTON_H, 2 * CHECK_H + 4)
    return top + gate + (GAP + 2) + folder + links + footer
