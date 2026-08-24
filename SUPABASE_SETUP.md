# Supabase Database Setup Required

## Create "guests" Table

Run this SQL in your Supabase SQL Editor:

```sql
-- Create guests table if it doesn't exist
CREATE TABLE IF NOT EXISTS guests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index on email for faster lookups (optional)
CREATE INDEX IF NOT EXISTS idx_guests_email ON guests(email);

-- Create an index on created_at for sorting (optional)
CREATE INDEX IF NOT EXISTS idx_guests_created_at ON guests(created_at);
```

## Permissions

Ensure Row Level Security (RLS) is configured appropriately:

```sql
-- Enable RLS
ALTER TABLE guests ENABLE ROW LEVEL SECURITY;

-- Allow inserting new guest records (public access)
CREATE POLICY "Allow public insert" ON guests
  FOR INSERT
  WITH CHECK (true);

-- Allow reading guest records (public access)
CREATE POLICY "Allow public read" ON guests
  FOR SELECT
  USING (true);

-- Optional: Prevent deletion/updates
CREATE POLICY "Prevent delete" ON guests
  FOR DELETE
  USING (false);
```

## Verification

After creating the table, test with:
```python
from database.supabase_client import supabase

# Test insert
response = supabase.table("guests").insert({
    "name": "Test Guest",
    "email": "test@example.com"
}).execute()

print(response.data)  # Should show inserted record with ID
```

