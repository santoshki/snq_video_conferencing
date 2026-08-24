from .supabase_client import supabase
import uuid


def create_guest_record(guest_name, guest_email=None):
    """
    Create a temporary guest record in the database.
    Returns guest_id if successful, None otherwise.
    """
    try:
        guest_name = guest_name.strip() if guest_name else ""
        if not guest_name:
            print("❌ Guest name is empty")
            return None

        guest_id = str(uuid.uuid4())
        print(f"\n📝 Attempting to create guest record:")
        print(f"   Name: {guest_name}")
        print(f"   Email: {guest_email if guest_email else '(not provided)'}")
        print(f"   Guest ID: {guest_id}")

        insert_data = {
            "id": guest_id,
            "name": guest_name,
            "email": guest_email.strip().lower() if guest_email else None,
        }
        print(f"   Data to insert: {insert_data}")

        response = (
            supabase
            .table("guests")
            .insert(insert_data)
            .execute()
        )

        print(f"   Response: {response}")
        print(f"   Response data: {response.data}")

        if response.data:
            print(f"✅ Guest record created successfully!")
            return guest_id

        print(f"⚠️  Response data is empty")
        return None

    except Exception as e:
        error_str = str(e)
        print("\n" + "="*70)
        print(f"❌ ERROR creating guest record: {error_str}")
        print("="*70)

        # Check if it's a missing table error
        if "does not exist" in error_str or "42P01" in error_str or "PGRST205" in error_str:
            print("\nProblem: Guests table does not exist in Supabase")
            print("\n✅ TO FIX:")
            print("   1. Open https://app.supabase.com/ → Your Project")
            print("   2. Click 'SQL Editor' → 'New Query'")
            print("   3. Copy & paste the SQL from: GUESTS_TABLE.sql")
            print("   4. Click 'Run'")
            print("   5. Restart your Flask app")
            print("\n📖 Full instructions: See FIX_GUESTS_TABLE.md")
        elif "permission" in error_str.lower():
            print("\nProblem: Permission denied - RLS policies may not be configured")
            print("\nCheck your Supabase RLS policies on the guests table")
        elif "connection" in error_str.lower():
            print("\nProblem: Database connection failed")
            print("Check your SUPABASE_URL and SUPABASE_KEY in .env file")

        print("="*70 + "\n")
        return None


def get_guest(guest_id):
    """
    Retrieve a guest record by ID.
    """
    try:
        response = (
            supabase
            .table("guests")
            .select("id, name, email")
            .eq("id", guest_id)
            .execute()
        )

        if response.data:
            return response.data[0]
        return None

    except Exception as e:
        print(f"Error retrieving guest: {e}")
        return None

