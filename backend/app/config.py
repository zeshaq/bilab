"""Configuration from environment, with sane local defaults for Phase 2."""
import os

CUBE_URL = os.environ.get("BILAB_CUBE_URL", "http://127.0.0.1:4199")
AUDIT_LOG = os.environ.get("BILAB_AUDIT_LOG", "/tmp/bilab-audit.log")
