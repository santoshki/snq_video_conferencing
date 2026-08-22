from werkzeug.security import check_password_hash
from .supabase_client import supabase


def authenticate_user(username, password):
    try:
        username = username.strip()
        response = (supabase.table("users")
            .select("*")
            .eq("username", username)
            .execute()
        )
        # User not found
        if not response.data:
            return None
        user = response.data[0]

        # Verify hashed password
        if check_password_hash(
            user["password_hash"],
            password
        ):
            return user

        return None

    except Exception as e:
        print("Authentication error:", e)
        return None