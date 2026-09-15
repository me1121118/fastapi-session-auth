import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi_session_auth import SessionMiddleware

def test_session_middleware():
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="test-secret-key-for-unit-testing")

    @app.post("/set")
    def set_val(req: Request):
        req.session["username"] = "john_doe"
        return {"ok": True}

    @app.get("/get")
    def get_val(req: Request):
        return {"user": req.session.get("username")}

    client = TestClient(app)
    res_set = client.post("/set")
    assert res_set.status_code == 200
    assert "session" in client.cookies

    res_get = client.get("/get")
    assert res_get.status_code == 200
    assert res_get.json()["user"] == "john_doe"
