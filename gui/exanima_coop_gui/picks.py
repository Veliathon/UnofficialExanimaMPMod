""












import re

_LOCAL_COPY = re.compile(r"\blocal copy (\d+)\b")


def local_copy_of(text):
    ""

    m = _LOCAL_COPY.search(text or "")
    return int(m.group(1)) if m else None


def free_bodies(roster):
    return [b for b in (roster or {}).get("bodies") or [] if b.get("free")]


def by_name(roster, name):
    ""
    n = (name or "").strip().lower()
    if not n:
        return None
    return next((b for b in free_bodies(roster) if (b.get("name") or "").strip().lower() == n), None)


def preselect(roster, last_name):
    ""

    if not roster or roster.get("pending"):
        return None
    b = by_name(roster, last_name)
    if b:
        return b
    free = free_bodies(roster)
    default_id = roster.get("default_id")
    b = next((x for x in free if default_id is not None and x.get("char_id") == default_id), None)
    return b or (free[0] if free else None)


def held_by_name(roster, name):
    ""


    n = (name or "").strip().lower()
    if not n or not roster or roster.get("pending"):
        return False
    return any((b.get("held_by") or "").strip().lower() == n for b in roster.get("bodies") or [] if not b.get("free"))


def same_bodies(a, b):
    ""

    def key(r):
        rows = [(x.get("char_id"), x.get("name"), x.get("free"), x.get("held_by"), x.get("state"), x.get("background")) for x in (r or {}).get("bodies") or []]
        return rows, (r or {}).get("level"), (r or {}).get("host_name")

    return key(a) == key(b)
