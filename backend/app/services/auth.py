"""Authentication against the lab's Keycloak realm (ADR-0007).

bilab owns no identity store: Keycloak is the identity plane and OPA (applied
at Trino) is the policy plane. The backend verifies the caller's Keycloak token
(signature, issuer, audience) and extracts the principal + groups, then passes
the token through to Cube so the same identity reaches Trino — one security
context for humans and agents.
"""
import jwt
from fastapi import HTTPException, Request
from jwt import PyJWKClient

from ..config import KEYCLOAK_AUDIENCE, KEYCLOAK_ISSUER, KEYCLOAK_JWKS_URL

_jwks = None


def _get_jwks():
    global _jwks
    if _jwks is None:
        _jwks = PyJWKClient(KEYCLOAK_JWKS_URL)
    return _jwks


def verify_token(token: str) -> dict:
    try:
        key = _get_jwks().get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            key.key,
            algorithms=["RS256"],
            audience=KEYCLOAK_AUDIENCE,
            issuer=KEYCLOAK_ISSUER,
            options={"verify_aud": True, "verify_iss": True, "require": ["exp"]},
        )
    except Exception as exc:  # any failure = unauthenticated
        raise HTTPException(status_code=401, detail="invalid or expired token") from exc


def get_identity(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    claims = verify_token(auth[7:])
    user = claims.get("preferred_username")
    if not user:
        raise HTTPException(status_code=401, detail="token has no principal")
    return {
        "user": user,
        "token": auth[7:],
        "groups": claims.get("groups") or [],
    }
