import os
from dotenv import load_dotenv

# Load a local .env for development. Production should set these through the
# service manager's EnvironmentFile instead.
load_dotenv()

APP_ENV = os.environ.get("APP_ENV", "production").strip().lower()
IS_PRODUCTION = APP_ENV == "production"


def _secret(name):
    value = os.environ.get(name, "")
    if value:
        if IS_PRODUCTION and len(value) < 32:
            raise RuntimeError(f"{name} must contain at least 32 characters in production")
        return value
    if IS_PRODUCTION:
        raise RuntimeError(f"{name} must be set in the production environment")
    # Development-only values prevent accidental use of known production keys.
    return f"development-only-{name}-do-not-deploy"


JWT_SECRET = _secret("JWT_SECRET")
JWT_ALGO = "HS256"
JWT_EXP_SECONDS = 3600  # 1 hour

FLASK_SECRET_KEY = _secret("FLASK_SECRET_KEY")

# Use a private coturn deployment or a managed TURN provider. Public shared
# relays are not reliable or safe for a consultation service.
_turn_urls = [url.strip() for url in os.environ.get("TURN_URLS", "").split(",") if url.strip()]
_turn_username = os.environ.get("TURN_USERNAME", "")
_turn_credential = os.environ.get("TURN_CREDENTIAL", "")

if IS_PRODUCTION and (not _turn_urls or not _turn_username or not _turn_credential):
    raise RuntimeError("TURN_URLS, TURN_USERNAME, and TURN_CREDENTIAL must be set in production")

ICE_SERVERS = [{"urls": "stun:stun.l.google.com:19302"}]
if _turn_urls and _turn_username and _turn_credential:
    ICE_SERVERS.append({
        "urls": _turn_urls,
        "username": _turn_username,
        "credential": _turn_credential,
    })
