""
















from collections import namedtuple

from . import steamjoin as SJ

FRIENDS_HINT = "Your friend must be on your Steam friends list."

CODE_HINT_AFTER_S = 60

Route = namedtuple("Route", "kind address error field")


def steam_ui_on(api_info):
    ""

    return isinstance(api_info, dict) and api_info.get("steam_connect") is True





ROUTE_STEAM, ROUTE_MANUAL = "steam", "manual"
STEAM_OFF = "This launcher can't use Steam connect. Use the Manual tab."
STEAM_MISSING = "Steam wasn't found on this PC, so the Steam way isn't available here. Use the Manual tab."
STEAM_HOST_TITLE = "Hosting through Steam"
STEAM_HOST_TEXT = ("No port forwarding and no password needed. Friends on your Steam friends list join from Steam (Join Game), "
                   "or with the join code shown here once your game runs. Under Invite only, just the friends you invite "
                   "in the game (F1) can join.")
STEAM_JOIN_TITLE = "Joining through Steam"
STEAM_JOIN_TEXT = ("Type the host's join code, or use Join Game on the host in your Steam friends list, or accept the "
                   "host's Steam invite. No port forwarding and no password needed. The host must be on your Steam "
                   "friends list, or have invited you.")


def steam_detected(gate):
    ""

    if not isinstance(gate, dict) or not gate.get("ok"):
        return False
    return gate.get("source") in ("steam_common", "steam_depot") or gate.get("steam_client") is True


def route_tabs(steam_ui, gate, manual=True):
    ""

    if not steam_ui:
        return False, "Steam", STEAM_OFF if manual else STEAM_OFF_ONLY
    if not steam_detected(gate):
        return False, "Steam", STEAM_MISSING if manual else STEAM_MISSING_ONLY
    return True, "Steam", None


def initial_route(steam_enabled, current=None, manual=True):
    ""


    if not manual:
        return ROUTE_STEAM
    if current == ROUTE_MANUAL or (current == ROUTE_STEAM and steam_enabled):
        return current
    return ROUTE_STEAM if steam_enabled else ROUTE_MANUAL






MANUAL_OFF = "Not available in this release. Host through Steam."






MANUAL_DISABLED_TITLE = "DISABLED"
MANUAL_DISABLED_TEXT = ("Manual connections are off in this first release. Use Steam: it needs no port forwarding or "
                        "network setup.")


def manual_off_shown(manual, route):
    ""

    return not manual and route == ROUTE_MANUAL
STEAM_OFF_ONLY = "This launcher can't use Steam connect, and joining by address is not available in this release."
STEAM_MISSING_ONLY = "Steam wasn't found on this PC. This release connects through Steam only: start Steam, then open the launcher again."


def manual_on(api_info):
    ""


    return not (isinstance(api_info, dict) and api_info.get("manual_connect") is False)


def manual_tab(manual):
    ""
    return (True, None) if manual else (False, MANUAL_OFF)


def greyed_note(value, steam_note, manual_note):
    ""
    if value == ROUTE_MANUAL:
        return manual_note
    if value == ROUTE_STEAM:
        return steam_note
    return steam_note or manual_note


def connect_possible(steam_ui, steam_enabled, manual, route):
    ""



    if route_direct(route) or not steam_ui:
        return bool(manual)
    return bool(steam_enabled) or bool(manual)


def route_direct(route):
    ""
    return route != ROUTE_STEAM


def password_shown(steam_ui, route):
    ""

    return not (bool(steam_ui) and route == ROUTE_STEAM)


def host_password_needed(steam_ui, direct):
    ""
    return not host_through_steam(steam_ui, direct)


def host_through_steam(steam_ui, direct):
    ""
    return bool(steam_ui) and not bool(direct)


def host_extra_opts(steam_ui, direct, access="invite"):
    ""

    if not host_through_steam(steam_ui, direct):
        return {}
    return {"steam": True, "steam_access": access_value(access)}




ACCESS_CHOICES = (("friends", "Friends"), ("invite", "Invite only"))
ACCESS_TIP = ("Who can join through Steam. Friends: any of your Steam friends (Join Game in their Steam friends list, "
              "or your join code). Invite only: only the friends you invite from the game (F1, Invite friends); nobody "
              "sees Join Game and a join code alone is not enough. No password is needed either way, and joining by "
              "address is off. You can switch while you play (F1).")


def access_value(v):
    ""

    return "friends" if v == "friends" else "invite"


def access_note(v):
    ""
    if access_value(v) == "invite":
        return ("Only the friends you invite get in: in the game press F1 and use Invite friends. Nobody sees Join Game, "
                "and a join code alone is not enough.")
    return ("Any of your Steam friends can join: Join Game in their Steam friends list, or your join code. The code "
            "shows here once the game runs.")


def join_route(steam_ui, direct, code_text, addr_text, password, manual=True):
    ""









    if not steam_ui or direct:
        if not manual:
            return Route("error", None, MANUAL_OFF, "code" if steam_ui else "addr")
        addr = (addr_text or "").strip()
        if not addr:
            return Route("error", None, "Type the host's address first (the IP the host gave you).", "addr")
        return Route("direct", addr, None, None)
    address, why = SJ.check_join_code_box(code_text, manual)
    if address is None:
        return Route("error", None, why, "code")
    return Route("steam", address, None, None)


def close_on_start_tip(steam_ui, manual=True):
    ""



    tip = ("Off: the launcher minimizes itself while you play and comes back when the game closes. "
           "On: it closes once the game has started. ")
    if not manual:
        if not steam_ui:
            return tip.rstrip()
        return tip + ("Hosting, it first shows your join code (it waits up to a minute for it) and closes 30 s later, so "
                      "you can copy it; the code is also in the game under the F1 panel.")
    if steam_ui:
        return tip + ("Hosting through Steam, it first shows your join code (it waits up to a minute for it) and closes "
                      "30 s later, so you can copy it; the code is also in the game under the F1 panel. Hosting the "
                      "manual way: your address and password are on the Manual tab before you start.")
    return tip + "As a host, your address and password are on the Manual tab: give them to your friends before you start."


def invite_code(steam_ui, lobby):
    ""

    if not steam_ui or lobby is None:
        return None
    return SJ.join_code("lobby", lobby)




GAME_STILL_OPEN = "Your game is still open: exit it first (Esc, then Exit), then press Connect."
INVITE_FROM_GAME = ("Steam invite from your running game: exit that game first (Esc, then Exit), then press Connect. "
                    "The game starts at its main menu and joins the host there.")

INVITE_READY = ("Steam invite: press Connect. The game starts at its main menu and joins the host there (CREATE makes "
                "your character, POSSESS takes your own).")




INVITE_WAITS_FOR_GAME = ("Steam invite received. Exit your game (Esc, then Exit): this window then opens the join form with "
                         "the host's join code.")
INVITE_AFTER_THIS = "Steam invite received: the join form with the host's join code opens once this join is over or cancelled."


def game_still_open(after_pid, alive):
    ""

    if after_pid is None:
        return None
    try:
        return GAME_STILL_OPEN if alive(after_pid) else None
    except Exception:
        return None


def advanced_label(open_, direct_on):
    ""
    arrow = "▾" if open_ else "▸"
    if direct_on and not open_:
        return "%s  Advanced  ·  direct connect" % arrow
    return "%s  Advanced" % arrow


def merge_host_status(state, st):
    ""





    state = dict(state or {})
    state.setdefault("code", None)
    state.setdefault("unavailable", False)
    st = st if isinstance(st, dict) else {}
    kind = st.get("state")
    if kind == "code":
        code = st.get("join_code")
        check, _ = SJ.parse_join_code(code) if isinstance(code, str) and code else (None, None)
        if check is not None:
            state["code"] = SJ.join_code(*check)
            state["unavailable"] = False
    elif kind == "unavailable":
        state["code"] = None
        state["unavailable"] = True
    return state


def host_code_done(state):
    ""

    return bool(state and (state.get("code") or state.get("unavailable")))





UNAVAILABLE_NOTE = ("Steam isn't available, so nobody can join this game. Close it and host from the Manual tab "
                    "(your friends choose Manual too).")

UNAVAILABLE_NOTE_ONLY = "Steam isn't available, so nobody can join this game. Close it, start Steam, then host again."


def host_code_view(state, waited_s, access="friends", manual=True):
    ""


    state = state or {}
    if state.get("code"):
        return state["code"], True, "Also shown in the game under the F1 panel.", False
    if state.get("unavailable"):
        return "not available", False, UNAVAILABLE_NOTE if manual else UNAVAILABLE_NOTE_ONLY, False
    if waited_s >= CODE_HINT_AFTER_S:
        return "not shown yet", False, "Press F1 in the game to see the join code.", False
    return "waiting for Steam…", False, "", False
