import os

# In production (Render) set these as real environment variables in the
# service dashboard. The literals below are only a fallback for local dev.
JWT_SECRET = os.environ.get("JWT_SECRET", "super_shared_secret_change_this")
JWT_ALGO = "HS256"
JWT_EXP_SECONDS = 3600  # 1 hour

FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "your_flask_session_secret")

# STUN alone is not enough once you have 3+ participants doing a full mesh
# of peer connections behind real-world NATs — some pairs simply won't find
# a direct route and that peer will silently never appear on screen. A TURN
# server relays media for those pairs. Openrelay is a free public TURN
# service that's fine for low-traffic/demo use; swap in your own
# (Twilio, Cloudflare, metered.ca, self-hosted coturn) before real traffic.
ICE_SERVERS = [
    {"urls": "stun:stun.l.google.com:19302"},
    {
        "urls": "turn:openrelay.metered.ca:80",
        "username": "openrelayproject",
        "credential": "openrelayproject",
    },
    {
        "urls": "turn:openrelay.metered.ca:443",
        "username": "openrelayproject",
        "credential": "openrelayproject",
    },
    {
        "urls": "turn:openrelay.metered.ca:443?transport=tcp",
        "username": "openrelayproject",
        "credential": "openrelayproject",
    },
]