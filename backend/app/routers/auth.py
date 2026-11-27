"""Login (Phase 3): exchange a username/password for a Keycloak token via the
resource-owner password grant, so the frontend can authenticate without a
browser OIDC redirect. The full OIDC flow is the Phase 3+ production path; this
is the internal-tool shortcut (same grant the lab's own tooling uses)."""
import json
import urllib.parse
import urllib.request

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config import KEYCLOAK_LOGIN_CLIENT_ID, KEYCLOAK_REALM, KEYCLOAK_URL

router = APIRouter(prefix="/api", tags=["auth"])


class Credentials(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(creds: Credentials):
    body = urllib.parse.urlencode({
        "grant_type": "password",
        "client_id": KEYCLOAK_LOGIN_CLIENT_ID,
        "username": creds.username,
        "password": creds.password,
    }).encode()
    try:
        with urllib.request.urlopen(
            urllib.request.Request(
                f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token",
                data=body,
            ),
            timeout=30,
        ) as r:
            data = json.load(r)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="login failed") from exc
    return {"token": data["access_token"], "token_type": data.get("token_type", "Bearer")}
