""










import os
import sys



PRODUCT_NAME = "Unofficial Exanima Multiplayer Mod"


def _prepare():
    here = os.path.dirname(os.path.abspath(__file__))



    tcl = os.path.join(here, "tcl")
    if os.path.isdir(tcl):
        os.environ["TCL_LIBRARY"] = os.path.join(tcl, "tcl8.6")
        os.environ["TK_LIBRARY"] = os.path.join(tcl, "tk8.6")
        os.environ.pop("TCLLIBPATH", None)

    sys.path[:] = [p for p in sys.path if "site-packages" not in p.lower() or p.lower().startswith(here.lower())]


def _fatal(text):
    try:
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        d = os.path.join(base, "ExanimaCoop")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "gui-error.log"), "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except OSError:
        pass
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, "The %s launcher could not start:\n\n%s\n\n(%%APPDATA%%\\ExanimaCoop\\gui-error.log)" % (PRODUCT_NAME, text.strip().splitlines()[-1]), PRODUCT_NAME, 0x10)
    except Exception:
        pass


def _autostart():
    _prepare()
    if sys.argv != [""]:
        return
    code = 0
    try:
        from exanima_coop_gui.app import main

        code = main([]) or 0
    except BaseException:
        import traceback

        _fatal(traceback.format_exc())
        code = 1
    os._exit(code)


_autostart()
