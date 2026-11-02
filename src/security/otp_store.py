# One-time sign-in codes, kept on the server.
#
# The code emailed to a user must never travel inside the token the app receives:
# a JWT is signed, not encrypted, so anything in it can be read. Instead we keep a
# hash of the code here, tied to the token it was issued with, and check it once.

import hashlib
import hmac
import secrets
import threading
import time

CODE_TTL_SECONDS = 10 * 60
MAX_ATTEMPTS = 5

_lock = threading.Lock()
_pending = {}  # email -> {"hash", "nonce", "expires", "attempts"}


def _hash(code: str) -> str:
    return hashlib.sha256(code.strip().lower().encode()).hexdigest()


def _key(email: str) -> str:
    return email.strip().lower()


def issue(email: str):
    """Create a code for this email. Returns (code, nonce); the nonce goes in the token."""
    code = secrets.token_hex(4)
    nonce = secrets.token_urlsafe(16)
    with _lock:
        _purge_expired()
        _pending[_key(email)] = {
            "hash": _hash(code),
            "nonce": nonce,
            "expires": time.time() + CODE_TTL_SECONDS,
            "attempts": 0,
        }
    return code, nonce


def verify(email: str, code: str, nonce: str) -> bool:
    """True once for the right code, from the token it was issued with, within 10 minutes."""
    if not email or not code or not nonce:
        return False
    with _lock:
        entry = _pending.get(_key(email))
        if not entry or entry["expires"] < time.time():
            _pending.pop(_key(email), None)
            return False
        if not hmac.compare_digest(entry["nonce"], nonce):
            return False
        entry["attempts"] += 1
        if hmac.compare_digest(entry["hash"], _hash(code)):
            del _pending[_key(email)]  # single use
            return True
        if entry["attempts"] >= MAX_ATTEMPTS:
            del _pending[_key(email)]  # too many tries: ask for a new code
        return False


def _purge_expired():
    now = time.time()
    for k in [k for k, v in _pending.items() if v["expires"] < now]:
        del _pending[k]
