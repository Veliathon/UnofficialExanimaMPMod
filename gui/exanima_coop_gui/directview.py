""












MANUAL_HINT = "Forward UDP 27500 on your router."

OPEN_PORT_LABEL = "Try to open the port on my router automatically"
OPEN_PORT_TIP = ("Asks your router to open UDP port 27500 for this PC while you host (UPnP, NAT-PMP or PCP), and closes it "
                 "again when the game or the launcher closes. Off by default: an open port can be reached from the whole "
                 "internet, exactly like a manual forward; the co-op mod's connection checks and your lobby password "
                 "protect it. Many routers do not offer this; then forward UDP 27500 on your router yourself. "
                 "Keep the launcher open while you host (minimized is fine): it keeps the opening alive.")


def open_port_applies(steam_ui, host_direct):
    ""
    return (not steam_ui) or bool(host_direct)


def keep_launcher_open(portmap_on):
    ""

    return bool(portmap_on)


def port_note(st, port=27500):
    ""
    st = st if isinstance(st, dict) else {}
    state = st.get("state")
    if state == "trying":
        return "Router: trying to open UDP port %d automatically…" % port, False
    if state == "open":
        how = st.get("protocol") or "the router"
        ext = st.get("external_port") or port
        if st.get("existing"):

            return ("Router: UDP port %d is already forwarded to this PC on your router (%s). The launcher leaves "
                    "that forward as it is." % (ext, how)), False
        if st.get("public") is False:
            return ("Router: port %d was opened (%s), but your router has no public address of its own (another router or "
                    "your internet provider sits in between), so friends probably still cannot reach you directly. %s"
                    % (ext, how, "Forward UDP 27500 on the router that has the public address." if ext == port else MANUAL_HINT)), True
        if ext != port:
            return ("Router: opened as port %d (%s). Friends type your public IP with :%d instead of :%d. "
                    "Closed again when the game or this launcher closes." % (ext, how, ext, port)), False
        return "Router: UDP port %d is open (%s). Closed again when the game or this launcher closes." % (port, how), False
    if state == "failed":
        why = (st.get("detail") or "").strip()
        return ("Router: the port could not be opened automatically%s. %s" % ((" (%s)" % why) if why else "", MANUAL_HINT)), True
    return "", False


CLOSE_TITLE = "Close the launcher?"


def close_note(st, port=27500):
    ""


    st = st if isinstance(st, dict) else {}
    if st.get("state") != "open" or st.get("existing"):
        return None
    ext = st.get("external_port") or port
    return ("Closing the launcher also closes UDP port %d on your router again. Your game keeps running; "
            "friends who have not joined yet would then need the port forwarded on your router.\n\n"
            "Close the launcher anyway?" % ext)


MANUAL_HOST_TITLE = "Hosting the manual way"
MANUAL_JOIN_TITLE = "Joining the manual way"
MANUAL_JOIN_TEXT = ("Type the address and the lobby password the host gave you. The host's UDP port 27500 must reach "
                    "their PC: the host forwards it on their router. Nothing to set up on your side.")


def forward_steps(gateway=None):
    ""

    where = "http://%s" % gateway if is_ipv4(gateway) else "your router's address, often http://192.168.0.1 or http://192.168.1.1"
    return ("To forward the port by hand: open your router's settings page in a browser (%s), find Port forwarding, "
            "and forward UDP port 27500 to this PC's LAN IP (listed above). Friends then join with your Public IP." % where)


def is_ipv4(s):
    ""
    if not isinstance(s, str):
        return False
    parts = s.strip().split(".")
    return len(parts) == 4 and all(p.isdigit() and len(p) <= 3 and int(p) <= 255 for p in parts)





ROUTER_CHECKING = "Checking your router…"
ROUTER_UNKNOWN = "Couldn't check automatically: forward UDP port 27500 by hand (see below)."
ROUTER_OK = ("Your router has its own public internet address, so forwarding UDP port 27500 on it should work "
             "(only a friend joining can prove it).")
ROUTER_DOUBLE = ("There is another router in front of yours: your router's own internet address is a private one. "
                 "Forward UDP port 27500 on both routers, or ask your provider to put the front one (often their modem) "
                 "in bridge mode.")


def _cgnat_way_out(steam_offered):
    if steam_offered:
        return "use Steam, or ask your provider for a public IP."
    return "ask your provider for a public IP, or let a friend host."


def router_note(check, public_ip=None, steam_offered=False):
    ""




    if check is None:
        return "checking", ROUTER_CHECKING
    if not isinstance(check, dict) or not check.get("ok") or check.get("state") != "answer" or not is_ipv4(check.get("external_ip")):
        return "unknown", ROUTER_UNKNOWN
    cls = check.get("class")
    if cls == "carrier":
        return "cgnat", ("Your internet provider shares your internet address with other customers (CGNAT). "
                         "Hosting the manual way won't work: " + _cgnat_way_out(steam_offered))
    if cls == "private":
        return "double", ROUTER_DOUBLE
    if cls != "public":
        return "unknown", ROUTER_UNKNOWN
    if is_ipv4(public_ip) and public_ip.strip() != check["external_ip"].strip():


        return "cgnat", ("Your router's internet address is not the one the internet sees, so your internet provider most "
                         "likely shares your address with other customers (CGNAT). Hosting the manual way probably won't work: "
                         + _cgnat_way_out(steam_offered))
    return "ok", ROUTER_OK







PUBLIC_LOOKUP_LABEL = "Show my public IP"
PUBLIC_LOOKUP_TIP = ("Asks an outside service (api.ipify.org) for your public address. Your IP address is sent to that "
                     "service. Only when you click.")
PUBLIC_ROW_TEXT = {"checking": "asking your router…", "looking": "asking…", "failed": "not available",
                   "none": "not available", "ask": ""}
LOOKUP_BUSY = "busy"


def looked_up_ip(lookup):
    ""

    if isinstance(lookup, dict) and lookup.get("ok") and is_ipv4(lookup.get("public_ip")):
        return lookup["public_ip"].strip()
    return None


def router_public_ip(check):
    ""
    if (isinstance(check, dict) and check.get("ok") and check.get("state") == "answer"
            and check.get("class") == "public" and is_ipv4(check.get("external_ip"))):
        return check["external_ip"].strip()
    return None


def public_row(check, router_busy=False, lookup=None, can_lookup=True):
    ""






    ip = looked_up_ip(lookup)
    if ip:
        return "looked_up", ip
    if lookup == LOOKUP_BUSY:
        return "looking", None
    if check is None or router_busy:
        return "checking", None
    ip = router_public_ip(check)
    if ip:
        return "router", ip
    if not can_lookup:
        return "none", None
    if isinstance(lookup, dict):
        return "failed", None
    return "ask", None


def ipv6_address(info):
    ""
    v6 = (info or {}).get("ipv6")
    if not isinstance(v6, str) or ":" not in v6 or any(c not in "0123456789abcdefABCDEF:." for c in v6):
        return None
    return "[%s]" % v6
