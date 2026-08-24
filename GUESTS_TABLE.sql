-- ============================================================================
-- Supabase SQL - Guests Table Creation
-- Copy & paste this entire block into Supabase SQL Editor
-- ============================================================================

-- Create guests table
CREATE TABLE IF NOT EXISTS guests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_guests_email ON guests(email);
CREATE INDEX IF NOT EXISTS idx_guests_created_at ON guests(created_at);

-- Enable Row Level Security
ALTER TABLE guests ENABLE ROW LEVEL SECURITY;

-- Allow anyone to insert new guests
CREATE POLICY "Allow public insert" ON guests
    FOR INSERT WITH CHECK (true);

-- Allow anyone to read guest records
CREATE POLICY "Allow public read" ON guests
    FOR SELECT USING (true);

-- ============================================================================
-- That's it! After running the above, you can verify with:
-- ============================================================================

-- Verify table was created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name = 'guests';

-- See any registered guests (will be empty at first)
SELECT * FROM guests;

-- Count total guests
SELECT COUNT(*) as total_guests FROM guests;

