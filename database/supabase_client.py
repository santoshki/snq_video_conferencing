import os
try:
    # dotenv is optional in deployed environments where env vars are set
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # If python-dotenv is not installed or .env not present, continue
    pass

from supabase import create_client, Client

_supabase_client = None

def get_supabase() -> Client:
    """Lazily create and return a Supabase client.

    This avoids creating network/SSL objects at import time which can
    cause compatibility issues in some hosting environments.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

    _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client
