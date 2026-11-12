""






import ctypes
import json
import os

DLL_NAME = "coop_launcher.dll"


PROGRESS_CB = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_char_p)


try:

    from . import devflags as _DEV
except ImportError:
    _DEV = None


def dll_candidates():
    ""



    here = os.path.dirname(os.path.abspath(__file__))
    bundled = os.path.join(os.path.dirname(here), DLL_NAME)
    if _DEV is None:
        return [bundled]
    return _DEV.dll_candidates(here, bundled, DLL_NAME)


def find_dll():
    for p in dll_candidates():
        if os.path.isfile(p):
            return p
    return None


def _b(s):
    return None if s is None else str(s).encode("utf-8")


class LauncherApi:
    def __init__(self, path=None):
        path = path or find_dll()
        if not path:
            raise OSError("%s not found (looked in: %s)" % (DLL_NAME, "; ".join(dll_candidates())))
        self.path = path
        lib = ctypes.CDLL(path)
        self.lib = lib
        cstr = ctypes.c_char_p
        for name, args in (
            ("coop_api_info", []),
            ("coop_game_check", [cstr]),
            ("coop_open_steam_console", []),
            ("coop_install_status", [cstr]),
            ("coop_install", [cstr]),
            ("coop_uninstall", [cstr]),
            ("coop_host_info", []),
            ("coop_fetch_roster", [cstr, cstr, cstr]),
            ("coop_download_save", [cstr, PROGRESS_CB, ctypes.c_void_p]),
            ("coop_start_host", [cstr]),
            ("coop_start_join", [cstr]),
            ("coop_join_status", [cstr, ctypes.c_uint64]),
            ("coop_host_status", [cstr, ctypes.c_uint32]),
            ("coop_portmap_start", [cstr]),
            ("coop_portmap_status", []),
            ("coop_portmap_stop", [ctypes.c_uint32]),
        ):
            f = getattr(lib, name)
            f.argtypes = args
            f.restype = ctypes.c_void_p

        self.has_depot_status = hasattr(lib, "coop_depot_status")
        if self.has_depot_status:
            lib.coop_depot_status.argtypes = [cstr]
            lib.coop_depot_status.restype = ctypes.c_void_p

        self.has_depot_prepare = hasattr(lib, "coop_depot_prepare") and hasattr(lib, "coop_depot_remove_old")
        if self.has_depot_prepare:
            lib.coop_depot_prepare.argtypes = []
            lib.coop_depot_prepare.restype = ctypes.c_void_p
            lib.coop_depot_remove_old.argtypes = [cstr]
            lib.coop_depot_remove_old.restype = ctypes.c_void_p


        self.has_uninstall_plan = hasattr(lib, "coop_uninstall_plan")
        if self.has_uninstall_plan:
            lib.coop_uninstall_plan.argtypes = [cstr]
            lib.coop_uninstall_plan.restype = ctypes.c_void_p


        self.has_router_check = hasattr(lib, "coop_router_check")
        if self.has_router_check:
            lib.coop_router_check.argtypes = []
            lib.coop_router_check.restype = ctypes.c_void_p


        self.has_public_lookup = hasattr(lib, "coop_public_ip_lookup")
        if self.has_public_lookup:
            lib.coop_public_ip_lookup.argtypes = []
            lib.coop_public_ip_lookup.restype = ctypes.c_void_p
        lib.coop_free.argtypes = [ctypes.c_void_p]
        lib.coop_free.restype = None
        lib.coop_cancel.argtypes = []
        lib.coop_cancel.restype = None
        lib.coop_process_alive.argtypes = [ctypes.c_uint32]
        lib.coop_process_alive.restype = ctypes.c_int32

    def _json(self, ptr):
        if not ptr:
            return {"ok": False, "kind": "internal", "error": "The launcher library returned nothing."}
        try:
            return json.loads(ctypes.string_at(ptr).decode("utf-8", "replace"))
        finally:
            self.lib.coop_free(ptr)



    def api_info(self):
        return self._json(self.lib.coop_api_info())

    def game_check(self, game_dir=None):
        return self._json(self.lib.coop_game_check(_b(game_dir)))

    def open_steam_console(self):
        return self._json(self.lib.coop_open_steam_console())

    def depot_status(self, game_dir=None):
        ""


        if not self.has_depot_status:
            return {"ok": False, "kind": "internal", "error": "This launcher library has no download watcher."}
        return self._json(self.lib.coop_depot_status(_b(game_dir)))

    def depot_prepare(self):
        ""

        if not self.has_depot_prepare:
            return None
        return self._json(self.lib.coop_depot_prepare())

    def depot_remove_old(self, path):
        ""
        if not self.has_depot_prepare:
            return {"ok": False, "kind": "internal", "error": "This launcher library cannot remove old copies."}
        return self._json(self.lib.coop_depot_remove_old(_b(path)))

    def install_status(self, game_dir):
        return self._json(self.lib.coop_install_status(_b(game_dir)))

    def install(self, game_dir):
        return self._json(self.lib.coop_install(_b(game_dir)))

    def uninstall_plan(self, game_dir):
        ""


        if not self.has_uninstall_plan:
            return {"ok": False, "kind": "internal", "error": "This launcher library cannot list the mod's files, so nothing is removed. Extract the whole download again."}
        return self._json(self.lib.coop_uninstall_plan(_b(game_dir)))

    def uninstall(self, game_dir):
        ""

        return self._json(self.lib.coop_uninstall(_b(game_dir)))

    def host_info(self):
        return self._json(self.lib.coop_host_info())

    def fetch_roster(self, addr, password, name):
        return self._json(self.lib.coop_fetch_roster(_b(addr), _b(password), _b(name)))

    def download_save(self, opts, progress=None):
        ""

        def cb(_user, received, total, text):
            if progress:
                try:
                    progress(received, total, text.decode("utf-8", "replace") if text else None)
                except Exception:
                    pass

        c_cb = PROGRESS_CB(cb)
        return self._json(self.lib.coop_download_save(_b(json.dumps(opts)), c_cb, None))

    def start_host(self, opts):
        return self._json(self.lib.coop_start_host(_b(json.dumps(opts))))

    def start_join(self, opts):
        return self._json(self.lib.coop_start_join(_b(json.dumps(opts))))

    def join_status(self, log_path, pos):
        return self._json(self.lib.coop_join_status(_b(log_path), int(pos)))

    def host_status(self, log_path, pid):
        ""

        return self._json(self.lib.coop_host_status(_b(log_path), int(pid) & 0xFFFFFFFF))




    def portmap_start(self, port=27500):
        return self._json(self.lib.coop_portmap_start(_b(json.dumps({"port": int(port)}))))

    def portmap_status(self):
        return self._json(self.lib.coop_portmap_status())

    def portmap_stop(self, wait_ms=1500):
        return self._json(self.lib.coop_portmap_stop(int(wait_ms)))

    def router_check(self):
        ""


        if not getattr(self, "has_router_check", False):
            return {"ok": False, "kind": "internal", "error": "This launcher library cannot check the router."}
        return self._json(self.lib.coop_router_check())

    def public_ip_lookup(self):
        ""


        if not getattr(self, "has_public_lookup", False):
            return {"ok": False, "kind": "internal", "error": "This launcher library cannot look up the public IP."}
        return self._json(self.lib.coop_public_ip_lookup())

    def process_alive(self, pid):
        return bool(self.lib.coop_process_alive(int(pid)))

    def cancel(self):
        self.lib.coop_cancel()
