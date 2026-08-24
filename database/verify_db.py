"""
Manual setup script for Supabase guests table.
This provides instructions and verification for database setup.
"""

from .supabase_client import get_supabase

def manual_setup_instructions():
    """Print instructions for manual table creation in Supabase."""
    instructions = """
╔════════════════════════════════════════════════════════════════╗
║          SUPABASE GUESTS TABLE SETUP                           ║
╚════════════════════════════════════════════════════════════════╝

To fix the "relation 'guests' does not exist" error:

STEP 1: Go to your Supabase Dashboard
   → Open your project
   → Click "SQL Editor" in the left sidebar
   → Click "New Query"

STEP 2: Copy and paste the SQL below:

─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS guests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_guests_email ON guests(email);
CREATE INDEX IF NOT EXISTS idx_guests_created_at ON guests(created_at);

ALTER TABLE guests ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public insert" ON guests
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read" ON guests
    FOR SELECT USING (true);
─────────────────────────────────────────────────────────────────

STEP 3: Click "Run" button

STEP 4: Verify success - you should see:
   ✓ "CREATE TABLE"
   ✓ "CREATE INDEX" (2 times)
   ✓ "ALTER TABLE"
   ✓ "CREATE POLICY" (2 times)

Then run the verification script below by executing:
   python verify_db.py

"""
    print(instructions)


def verify_table_exists():
    """Verify the guests table exists and is accessible."""
    try:
        # Try to query the guests table
        supabase = get_supabase()
        response = supabase.table("guests").select("count").limit(1).execute()
        print("✓ SUCCESS: Guests table exists and is accessible!")
        print(f"  Response: {response}")
        return True
    except Exception as e:
        error_str = str(e)
        if "does not exist" in error_str or "42P01" in error_str:
            print("✗ FAILED: Guests table does not exist")
            print(f"  Error: {e}")
            print("\n  Please follow the setup instructions above.")
            return False
        else:
            print(f"? UNKNOWN ERROR: {e}")
            return False


if __name__ == "__main__":
    print("\n")
    manual_setup_instructions()
    print("\n" + "─" * 66)
    print("Verifying database setup...\n")
    verify_table_exists()

