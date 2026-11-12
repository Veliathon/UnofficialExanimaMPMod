""










import secrets

ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"
GROUPS = 3
GROUP_LEN = 4


def random_password():
    ""
    return "-".join("".join(secrets.choice(ALPHABET) for _ in range(GROUP_LEN)) for _ in range(GROUPS))


def looks_generated(p):
    ""
    parts = (p or "").split("-")
    return len(parts) == GROUPS and all(len(g) == GROUP_LEN and all(c in ALPHABET for c in g) for g in parts)
