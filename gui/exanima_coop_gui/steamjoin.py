""











import re

LOBBY_PREFIX = "steamlobby:"
HOST_PREFIX = "steam:"



_CODE_GROUP = re.compile(r"^[0-9A-Za-z]{1,4}$")


def is_lobby_id(n):
    ""

    return (isinstance(n, int) and 0 < n < (1 << 64) and n >> 56 == 1 and (n >> 52) & 0xF == 8
            and (n >> 32) & 0x40000 != 0 and n & 0xFFFFFFFF != 0)


def _digits(s):
    ""
    if not isinstance(s, str) or not (1 <= len(s) <= 20) or not all("0" <= c <= "9" for c in s):
        return None
    return int(s)


def parse_join_lobby(argv):
    ""

    argv = list(argv or [])
    hits = [i for i, a in enumerate(argv) if a == "--join-lobby"]
    if len(hits) != 1 or hits[0] + 1 >= len(argv):
        return None
    n = _digits(argv[hits[0] + 1])
    return n if n is not None and is_lobby_id(n) else None


def parse_after_game(argv):
    ""


    argv = list(argv or [])
    hits = [i for i, a in enumerate(argv) if a == "--after-game"]
    if len(hits) != 1 or hits[0] + 1 >= len(argv):
        return None
    s = argv[hits[0] + 1]
    if not isinstance(s, str) or not (1 <= len(s) <= 10) or not all("0" <= c <= "9" for c in s):
        return None
    n = int(s)
    return n if 0 < n < (1 << 32) else None


def lobby_address(lobby):
    return "%s%d" % (LOBBY_PREFIX, lobby)


def looks_like_join_code(text):
    groups = (text or "").strip().split("-")
    n = sum(len(g) for g in groups)
    return (len(groups) >= 2 and n in (8, 14) and all(len(g) == 4 for g in groups[:-1])
            and all(_CODE_GROUP.match(g) for g in groups))


def is_steam_join(text):
    ""

    t = (text or "").strip()
    low = t.lower()
    for prefix in (LOBBY_PREFIX, HOST_PREFIX):
        if low.startswith(prefix):
            return _digits(t[len(prefix):]) is not None
    return looks_like_join_code(t)







ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
SHORT_LEN = 8
LONG_LEN = 14
KIND_LOBBY = 0
KIND_HOST = 1
CRC_INIT = 0x15
LOBBY_UPPER = 0x01860000
INDIVIDUAL_UPPER = 0x01100001


CODE_LENGTH = "a join code has 8 characters (like ABCD-1234)"
CODE_CHARACTER = "a join code has only the letters and digits the host's game shows"
CODE_INVALID = "that join code is not valid: check it for a typo"


def is_individual(n):
    ""
    return isinstance(n, int) and 0 < n < (1 << 64) and n >> 56 == 1 and (n >> 52) & 0xF == 1 and n & 0xFFFFFFFF != 0


def crc6(v, nbits):
    ""
    r = CRC_INIT
    for i in range(nbits - 1, -1, -1):
        bit = (v >> i) & 1
        top = (r >> 5) & 1
        r = (r << 1) & 0x3F
        if top ^ bit:
            r ^= 0x03
    return r


def _to_base32(v, chars):
    return "".join(ALPHABET[(v >> (5 * i)) & 31] for i in range(chars - 1, -1, -1))


def _group(s):
    return "-".join(s[i:i + 4] for i in range(0, len(s), 4))


def join_code(kind, ident):
    ""

    if kind == "lobby" and is_lobby_id(ident):
        k, upper = KIND_LOBBY, LOBBY_UPPER
    elif kind == "host" and is_individual(ident):
        k, upper = KIND_HOST, INDIVIDUAL_UPPER
    else:
        return None
    if ident >> 32 == upper:
        payload = k << 32 | (ident & 0xFFFFFFFF)
        return _group(_to_base32(payload << 6 | crc6(payload, 34), SHORT_LEN))
    return _group(_to_base32(ident << 6 | crc6(ident, 64), LONG_LEN))


def parse_join_code(text):
    ""

    v = 0
    n = 0
    for c in (text or "").strip():
        if c in "- ":
            continue
        if "a" <= c <= "z":
            c = c.upper()
        c = {"O": "0", "I": "1", "L": "1"}.get(c, c)
        d = ALPHABET.find(c) if len(c) == 1 else -1
        if d < 0:
            return None, CODE_CHARACTER
        n += 1
        if n > LONG_LEN:
            return None, CODE_LENGTH
        v = v << 5 | d
    if n == SHORT_LEN:
        payload = v >> 6
        if crc6(payload, 34) != v & 0x3F:
            return None, CODE_INVALID
        account = payload & 0xFFFFFFFF
        kind = payload >> 32
        if kind == KIND_LOBBY:
            t = ("lobby", LOBBY_UPPER << 32 | account)
            ok = is_lobby_id(t[1])
        elif kind == KIND_HOST:
            t = ("host", INDIVIDUAL_UPPER << 32 | account)
            ok = is_individual(t[1])
        else:
            return None, CODE_INVALID
        return (t, None) if ok else (None, CODE_INVALID)
    if n == LONG_LEN:
        ident = v >> 6
        if crc6(ident, 64) != v & 0x3F:
            return None, CODE_INVALID
        if is_lobby_id(ident):
            return ("lobby", ident), None
        if is_individual(ident):
            return ("host", ident), None
        return None, CODE_INVALID
    return None, CODE_LENGTH


def target_address(target):
    ""
    kind, ident = target
    return "%s%d" % (LOBBY_PREFIX if kind == "lobby" else HOST_PREFIX, ident)


def parse_steam_address(text):
    ""

    t = (text or "").strip()
    low = t.lower()
    if low.startswith(LOBBY_PREFIX):
        n = _digits(t[len(LOBBY_PREFIX):])
        return ("lobby", n) if n is not None and is_lobby_id(n) else None
    if low.startswith(HOST_PREFIX):
        n = _digits(t[len(HOST_PREFIX):])
        return ("host", n) if n is not None and is_individual(n) else None
    return None





_DASHES = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\ufe58\ufe63\uff0d"
_INVISIBLE = "\u200b\u200c\u200d\u2060\ufeff\u00ad"


def clean_pasted(text):
    ""

    t = text or ""
    for c in _INVISIBLE:
        t = t.replace(c, "")
    for c in _DASHES:
        t = t.replace(c, "-")
    t = re.sub(r"\s+", " ", t).strip()
    return t.strip("`'\"\u2018\u2019\u201c\u201d").strip()


def find_join_code(text):
    ""

    for w in re.split(r"[^0-9A-Za-z-]+", clean_pasted(text)):
        w = w.strip("-")
        if looks_like_join_code(w) and parse_join_code(w)[0] is not None:
            return w.upper()
    return None


def check_join_code_box(text, manual=True):
    ""



    t = clean_pasted(text)
    if not t:
        return None, "Type the host's join code first (it looks like ABCD-1234)."
    target = parse_steam_address(t)
    if target is not None:
        return target_address(target), None
    found = find_join_code(t)
    if any(c in t for c in ".:[]") and found is None:
        if not manual:
            return None, "That looks like an address. Joining by address is not available in this release: type the host's join code."
        return None, "That looks like an address. Joining by address is on the Manual tab."
    target, why = parse_join_code(t)
    if target is None and found is not None:
        target, why = parse_join_code(found)
    if target is None:
        return None, "Join code: %s." % why
    return target_address(target), None


def display_code(address):
    ""
    target = parse_steam_address(address)
    return join_code(*target) if target else None
