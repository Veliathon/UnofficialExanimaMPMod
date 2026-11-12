""












POLL_MS = 700


POLL_HIDDEN_MS = 2000


def after_start(close_on_start, warnings, wait_for_code=False):
    ""













    if warnings:
        return "stay"
    if wait_for_code:
        return "wait_code"
    if close_on_start:
        return "close"
    return "minimize"




CODE_WAIT_S = 60


CODE_CLOSE_GRACE_S = 30


def after_code_wait(close_on_start, code_settled, waited_s, settled_for_s=0):
    ""



    if code_settled:
        if not close_on_start:
            return "minimize"
        if settled_for_s >= CODE_CLOSE_GRACE_S or waited_s >= CODE_WAIT_S + CODE_CLOSE_GRACE_S:
            return "close"
        return None
    if waited_s >= CODE_WAIT_S:
        return "close" if close_on_start else "minimize"
    return None


def restore_on_outcome(outcome):
    ""


    return outcome in ("refused", "full", "timeout")



JOIN_TIMEOUT_S = 180







BEGIN_SHOWN = (
    "BEGIN is ", "BEGIN pressed", "the new-game hook ", "the creator's ", "a new story was about to start",
    "our character", "our new character", "our copy of", "this level is map", "an answer for request",
    "the host did not answer our new character", "the host waits for space", "the host made our character",
    "the host refused our character",
)


def join_progress_line(line):
    ""


    line = (line or "").strip()
    if not line:
        return False
    if "welcomed by " in line or "host says" in line or " begin: " in line or line.startswith("begin: "):
        return True
    return line.startswith(BEGIN_SHOWN)


def join_timed_out(new_char, elapsed, progressed):
    ""





    if new_char and progressed:
        return False
    return elapsed > JOIN_TIMEOUT_S


def poll_ms(minimized):
    ""
    return POLL_HIDDEN_MS if minimized else POLL_MS
