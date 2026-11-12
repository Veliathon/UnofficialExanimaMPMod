""







PRODUCT_NAME = "Unofficial Exanima Multiplayer Mod"
PUBLISHER = "Veliathon"
COPYRIGHT = "© 2026 Veliathon"
NOT_AFFILIATED = "Not affiliated with or endorsed by Bare Mettle Entertainment."
LEGITIMATE_COPY = "Requires your own legitimate copy of Exanima."


BRANDING_LINE = "%s by %s. %s %s" % (PRODUCT_NAME, PUBLISHER, NOT_AFFILIATED, LEGITIMATE_COPY)



PRIVACY_POINTER = "Privacy: see PRIVACY.md in the mod's folder (also on the mod's page)."

ABOUT_TIP = "%s %s" % (BRANDING_LINE, PRIVACY_POINTER)




HEADER_PARTS = ((PRODUCT_NAME, "accent"),)
SUBTITLE = ""


def about_line(mod_version=None):
    ""
    v = (mod_version or "").strip()
    return "%s%s  ·  %s" % (PRODUCT_NAME, " " + v if v else "", COPYRIGHT)



PUBLIC_PACKAGE = "public"


def _build_id(info):
    b = info.get("build") if isinstance(info, dict) else None
    return str(b).strip() if b else ""


def identity_line(info, package=None):
    ""



    info = info if isinstance(info, dict) else {}
    game = str(info.get("game_version") or "").strip()
    if game.startswith("V "):
        game = game[2:].strip()
    return "Build %s · game %s · %s" % (_build_id(info) or "unknown", game or "unknown", (package or "").strip() or PUBLIC_PACKAGE)


def window_title(info):
    ""
    b = _build_id(info)
    return "%s  ·  build %s" % (PRODUCT_NAME, b) if b else PRODUCT_NAME
