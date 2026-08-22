from .supabase_client import supabase


def authenticate_user(username, password):
    try:
        username = username.strip()

        # Find the user's email from your profile table
        response = (
            supabase
            .table("users")
            .select("id, first_name, last_name, email, username")
            .eq("username", username)
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