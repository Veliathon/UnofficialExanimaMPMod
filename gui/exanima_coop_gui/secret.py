""













import base64
import sys


ENTROPY = b"ExanimaCoop.launcher.remembered-password.v1"
CRYPTPROTECT_UI_FORBIDDEN = 0x1

BLOB_MAX = 8192

_api = None


def _load():
    global _api
    if _api is not None:
        return _api
    _api = False
    if sys.platform != "win32":
        return _api
    try:
        import ctypes
        from ctypes import wintypes

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

        crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        proto = [ctypes.POINTER(DATA_BLOB), wintypes.LPCWSTR, ctypes.POINTER(DATA_BLOB), ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(DATA_BLOB)]
        crypt32.CryptProtectData.argtypes = proto
        crypt32.CryptProtectData.restype = wintypes.BOOL
        crypt32.CryptUnprotectData.argtypes = [ctypes.POINTER(DATA_BLOB), ctypes.c_void_p] + proto[2:]
        crypt32.CryptUnprotectData.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p
        _api = (ctypes, crypt32, kernel32, DATA_BLOB)
    except (ImportError, OSError, AttributeError):
        _api = False
    return _api


def available():
    ""
    return bool(_load())


def _call(fn_name, data, entropy):
    ""
    api = _load()
    if not api:
        return None
    ctypes, crypt32, kernel32, DATA_BLOB = api
    buf = ctypes.create_string_buffer(data, len(data) or 1)
    din = DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte)))
    ebuf = ctypes.create_string_buffer(entropy, len(entropy) or 1)
    dent = DATA_BLOB(len(entropy), ctypes.cast(ebuf, ctypes.POINTER(ctypes.c_ubyte)))
    dout = DATA_BLOB()
    fn = getattr(crypt32, fn_name)
    if not fn(ctypes.byref(din), None, ctypes.byref(dent), None, None, CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(dout)):
        return None
    try:
        return ctypes.string_at(dout.pbData, dout.cbData)
    finally:
        if dout.pbData:

            if fn_name == "CryptUnprotectData":
                ctypes.memset(dout.pbData, 0, dout.cbData)
            kernel32.LocalFree(ctypes.cast(dout.pbData, ctypes.c_void_p))


def protect(text, entropy=ENTROPY):
    ""

    if not text:
        return ""
    try:
        out = _call("CryptProtectData", text.encode("utf-8"), entropy)
    except Exception:
        return None
    if out is None:
        return None
    return base64.b64encode(out).decode("ascii")


def unprotect(blob, entropy=ENTROPY):
    ""

    if not isinstance(blob, str) or not blob or len(blob) > BLOB_MAX:
        return ""
    try:
        raw = base64.b64decode(blob.encode("ascii"), validate=True)
        out = _call("CryptUnprotectData", raw, entropy)
        return out.decode("utf-8") if out is not None else ""
    except Exception:
        return ""
