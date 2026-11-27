"""Configuration from environment, with sane local defaults."""
import os

CUBE_URL = os.environ.get("BILAB_CUBE_URL", "http://127.0.0.1:4199")
AUDIT_LOG = os.environ.get("BILAB_AUDIT_LOG", "/tmp/bilab-audit.log")

# Keycloak (lab realm) — identity plane for bilab (ADR-0007).
KEYCLOAK_URL = os.environ.get("BILAB_KEYCLOAK_URL", "http://localhost:8180")
KEYCLOAK_REALM = os.environ.get("BILAB_KEYCLOAK_REALM", "datalab")
KEYCLOAK_JWKS_URL = os.environ.get(
    "BILAB_KEYCLOAK_JWKS_URL",
    "http://localhost:8180/realms/datalab/protocol/openid-connect/certs",
)
KEYCLOAK_ISSUER = os.environ.get(
    "BILAB_KEYCLOAK_ISSUER", "http://localhost:8180/realms/datalab"
)
KEYCLOAK_AUDIENCE = os.environ.get("BILAB_KEYCLOAK_AUDIENCE", "trino")
# Client used for the resource-owner (password) login flow in Phase 3.
KEYCLOAK_LOGIN_CLIENT_ID = os.environ.get("BILAB_KEYCLOAK_LOGIN_CLIENT_ID", "datalab-cli")
