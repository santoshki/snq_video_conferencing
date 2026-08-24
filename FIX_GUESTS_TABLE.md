# ⚠️ CRITICAL: Create Guests Table in Supabase

## The Error
```
ERROR: 42P01: relation "guests" does not exist
```

This means the `guests` table hasn't been created in your Supabase database yet.

---

## ✅ Quick Fix (2 minutes)

### Step 1: Open Supabase SQL Editor
1. Go to https://app.supabase.com/
2. Select your project
3. Click **SQL Editor** (left sidebar)
4. Click **New Query**

### Step 2: Copy & Paste This SQL
```sql
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

-- Enable security
ALTER TABLE guests ENABLE ROW LEVEL SECURITY;

-- Allow anyone to insert new guests
CREATE POLICY "Allow public insert" ON guests
    FOR INSERT WITH CHECK (true);

-- Allow anyone to read guest records
CREATE POLICY "Allow public read" ON guests
    FOR SELECT USING (true);
```

### Step 3: Click Run
You should see these messages appear:
- ✓ CREATE TABLE
- ✓ CREATE INDEX
- ✓ CREATE INDEX
- ✓ ALTER TABLE
- ✓ CREATE POLICY
- ✓ CREATE POLICY

### Step 4: Verify (Optional)
Run this in a new query to confirm:
```sql
SELECT COUNT(*) as guest_count FROM guests;
```

Should return 0 (empty table is OK).

---

## ✅ After Setup

Once the table is created, restart your Flask app:

```powershell
# In your project directory
python app.py
```

Then test by:
1. Open http://localhost:5000 in browser
2. Try joining a meeting without logging in
3. You should see the guest registration form
4. After registering, you'll join the meeting

---

## 🔍 Troubleshooting

### Still seeing "relation does not exist" error?
- ✓ Check you ran ALL the SQL above (not just CREATE TABLE)
- ✓ Make sure you're in the correct Supabase project
- ✓ Try refreshing the page
- ✓ Restart your Flask app

### Need to verify the table exists?
Run in Supabase SQL Editor:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'guests';
```

Should return one row with `guests`.

### Want to see existing guest records?
```sql
SELECT * FROM guests;
```

---

## 📝 Table Schema Reference

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | Auto-generated, unique ID |
| `name` | TEXT | Guest's display name (required) |
| `email` | TEXT | Guest's email (optional) |
| `created_at` | TIMESTAMP | When they registered |


