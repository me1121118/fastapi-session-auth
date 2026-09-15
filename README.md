# fastapi-session-auth

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/fastapi-session-auth/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Secure, tamper-proof signed cookie session middleware for FastAPI and Starlette with HMAC-SHA256 integrity verification.

---

## 🚀 Features

- 🔐 **Tamper-Proof Signing**: Cryptographically signed cookie sessions with secret keys.
- 🍪 **SameSite & HttpOnly**: Configured with production-ready security defaults.
- ⚡ **Zero DB Overhead**: Stores session data client-side in signed cookies.

---

## 📦 Installation

```bash
pip install fastapi-session-auth
```

---

## 🛠️ Quickstart

```python
from fastapi import FastAPI, Request
from fastapi_session_auth import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-super-secret-key-32-chars-long")

@app.post("/login")
def login(request: Request):
    request.session["user_id"] = 42
    return {"message": "Logged in"}

@app.get("/me")
def me(request: Request):
    return {"user_id": request.session.get("user_id")}
```

---

## ☕ Support My Studies / Buy Me a Coffee

I am an independent developer and student building open-source developer productivity tools. If this session middleware simplified your auth, please consider supporting my studies:

- ☕ **Buy Me a Coffee:** [ko-fi.com/me1121118](https://ko-fi.com/)
- ⭐ **Star this repository** on GitHub!

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
