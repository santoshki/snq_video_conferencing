"""
Database initialization script to create required tables in Supabase.
Run this once to set up the database schema.
"""

from .supabase_client import get_supabase

def init_guests_table():
    """
    Create the guests table in Supabase if it doesn't exist.
    This function uses Supabase's SQL interface via the admin API.
    """
    try:
        # Create guests table using SQL
        sql_query = """
        CREATE TABLE IF NOT EXISTS guests (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_guests_email ON guests(email);
        CREATE INDEX IF NOT EXISTS idx_guests_created_at ON guests(created_at);
        """

        # Use Supabase's RPC or direct SQL execution
        # Note: This requires service role key, not anon key
        supabase = get_supabase()
        response = supabase.query(sql_query)
        print("✓ Guests table created successfully")
        return True

    except Exception as e:
        error_msg = str(e)
        # Check if table already exists
        if "already exists" in error_msg or "duplicate" in error_msg.lower():
            print("✓ Guests table already exists")
            return True
        else:
            print(f"✗ Error creating guests table: {e}")
            print("\nPlease create the table manually in Supabase SQL Editor:")
            print("""
            CREATE TABLE IF NOT EXISTS guests (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """)
            return False


def init_rls_policies():
    """
    Initialize Row Level Security (RLS) policies for the guests table.
    """
    try:
        # Enable RLS
        supabase = get_supabase()
        supabase.query("ALTER TABLE guests ENABLE ROW LEVEL SECURITY;")

        # Allow public insert
        supabase.query("""
        CREATE POLICY "Allow public insert" ON guests
            FOR INSERT
            WITH CHECK (true);
        """)

        # Allow public read
        supabase.query("""
        CREATE POLICY "Allow public read" ON guests
            FOR SELECT
            USING (true);
        """)

        print("✓ RLS policies configured successfully")
        return True

    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            print("✓ RLS policies already configured")
            return True
        else:
            print(f"Note: RLS policies may need manual configuration: {e}")
            return False


def verify_guests_table():
    """
    Verify that the guests table exists and is accessible.
    """
    try:
        supabase = get_supabase()
        response = supabase.table("guests").select("*").limit(0).execute()
        print("✓ Guests table is accessible and working")
        return True
    except Exception as e:
        print(f"✗ Error accessing guests table: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Database Initialization")
    print("=" * 50)

    # Try to create table
    print("\n1. Creating guests table...")
    table_created = init_guests_table()

    # Try to initialize RLS
    print("\n2. Configuring RLS policies...")
    rls_configured = init_rls_policies()

    # Verify
    print("\n3. Verifying table...")
    table_verified = verify_guests_table()

    print("\n" + "=" * 50)
    if table_created and table_verified:
        print("✓ Database setup complete!")
    else:
        print("⚠ Some setup steps need manual configuration.")
        print("See SUPABASE_SETUP.md for manual SQL commands.")
    print("=" * 50)
