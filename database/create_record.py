from .supabase_client import get_supabase


def check_user(email, username):
    supabase = get_supabase()
    existing_user = (
        supabase
        .table("users")
        .select("id, email, username")
        .or_(f"email.eq.{email},username.eq.{username}")
        .execute()
    )

    if existing_user.data:
        return existing_user.data[0]

    return None


def create_user_record(
    first_name,
    last_name,
    email,
    username,
    password
):
    try:
        email = email.strip().lower()
        username = username.strip()

        # Check if profile already exists
        existing_user = check_user(email, username)

        if existing_user:
            return None

        supabase = get_supabase()
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if not auth_response.user:
            return None

        auth_user_id = auth_response.user.id


        response = (
            supabase
            .table("users")
            .insert({
                "id": auth_user_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "username": username
            })
            .execute()
        )

        if response.data:
            return response.data[0]["id"]

        # If profile creation failed, return None.
        # Auth user may need cleanup through an admin/service-role
        # operation if you want complete rollback behavior.
        return None

    except Exception as e:
        print(f"Error creating user: {e}")
        return None