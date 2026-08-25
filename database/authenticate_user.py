from .supabase_client import get_supabase


def authenticate_user(credential, password):
    """
    Authenticate user via username or email.

    Args:
        credential: Username or email address
        password: User password

    Returns:
        User object if authentication succeeds, None otherwise
    """
    try:
        credential = credential.strip().lower()

        # Find the user by username or email
        supabase = get_supabase()
        response = (
            supabase
            .table("users")
            .select("id, first_name, last_name, email, username")
            .or_(f"username.eq.{credential},email.eq.{credential}")
            .execute()
        )

        if not response.data:
            return None

        user = response.data[0]
        email = user["email"]

        # Authenticate using Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if not auth_response.user:
            return None

        # Return your application user/profile
        return user

    except Exception as e:
        print("Authentication error:", e)
        return None