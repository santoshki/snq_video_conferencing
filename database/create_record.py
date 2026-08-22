from werkzeug.security import generate_password_hash
from .supabase_client import supabase


def check_user(email, username):

    existing_user = (
        supabase
        .table("users")
        .select("id")
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

    # Check if user already exists
    existing_user = check_user(email, username)

    if existing_user:
        return None

    # Hash password
    password_hash = generate_password_hash(password)

    # Insert into Supabase
    response = (
        supabase
        .table("users")
        .insert({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": username,
            "password_hash": password_hash
        })
        .execute()
    )

    if response.data:
        return response.data[0]["id"]

    return None