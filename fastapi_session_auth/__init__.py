import base64
import hashlib
import hmac
import json
from typing import Dict, Any, Optional
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send

class SessionMiddleware:
    """
    ASGI middleware for client-side cryptographically signed cookie sessions.
    """

    def __init__(
        self,
        app: ASGIApp,
        secret_key: str,
        session_cookie: str = "session",
        max_age: int = 14 * 24 * 3600,
        same_site: str = "lax",
        https_only: bool = False,
    ):
        self.app = app
        self.secret_key = secret_key.encode("utf-8")
        self.session_cookie = session_cookie
        self.max_age = max_age
        self.same_site = same_site
        self.https_only = https_only

    def _sign(self, data: bytes) -> bytes:
        b64_data = base64.urlsafe_b64encode(data)
        sig = hmac.new(self.secret_key, b64_data, hashlib.sha256).digest()
        b64_sig = base64.urlsafe_b64encode(sig)
        return b64_data + b"." + b64_sig

    def _unsign(self, signed_data: str) -> Optional[bytes]:
        try:
            b64_data, b64_sig = signed_data.encode("ascii").split(b".", 1)
            expected_sig = hmac.new(self.secret_key, b64_data, hashlib.sha256).digest()
            actual_sig = base64.urlsafe_b64decode(b64_sig)
            if hmac.compare_digest(actual_sig, expected_sig):
                return base64.urlsafe_b64decode(b64_data)
        except Exception:
            return None
        return None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # Load session from cookie
        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie", b"").decode("latin1")
        session_data: Dict[str, Any] = {}

        if cookie_header:
            from http.cookies import SimpleCookie
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            if self.session_cookie in cookie:
                unsigned = self._unsign(cookie[self.session_cookie].value)
                if unsigned:
                    try:
                        session_data = json.loads(unsigned.decode("utf-8"))
                    except Exception:
                        session_data = {}

        scope["session"] = session_data

        async def send_wrapper(message: dict) -> None:
            if message["type"] == "http.response.start":
                serialized = json.dumps(scope["session"]).encode("utf-8")
                signed_cookie = self._sign(serialized).decode("ascii")
                cookie_str = (
                    f"{self.session_cookie}={signed_cookie}; "
                    f"Max-Age={self.max_age}; Path=/; SameSite={self.same_site}"
                )
                if self.https_only:
                    cookie_str += "; Secure"

                res_headers = MutableHeaders(raw=list(message.get("headers", [])))
                res_headers.append("set-cookie", cookie_str)
                message["headers"] = res_headers.raw

            await send(message)

        await self.app(scope, receive, send_wrapper)
