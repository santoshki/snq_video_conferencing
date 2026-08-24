# 🔧 Troubleshooting: "Failed to register as guest"

## What This Error Means
The guest registration is failing at the database layer. This could be due to several reasons.

## Diagnostic Steps

### Step 1: Check Flask Terminal Output
When you try to register as a guest, watch your Flask terminal. You should see debug output like:

```
🔵 Guest registration attempt:
   Name: John Doe
   Email: john@example.com
   Room: abc-123-def
📤 Calling create_guest_record...
📝 Attempting to create guest record:
   Name: John Doe
   Email: john@example.com
   Guest ID: xxxxx-xxxxx-xxxxx
   Data to insert: {...}
   Response: ...
✅ Guest record created successfully!
```

**If you see this ✅, registration is working!**

---

## Common Errors & Fixes

### Error 1: "relation 'guests' does not exist"
```
ERROR 42P01: relation "guests" does not exist
```

**Fix**: The guests table hasn't been created in Supabase

1. Open https://app.supabase.com/ → Your Project
2. Click **SQL Editor** → **New Query**
3. Copy all SQL from `GUESTS_TABLE.sql` file
4. Click **Run**
5. Restart Flask app

---

### Error 2: "permission denied" or "violates row level security"
```
ERROR: new row violates row level security policy
```

**Fix**: RLS policies aren't configured correctly

1. Go to Supabase → **Table Editor**
2. Select the `guests` table
3. Click **Policies** tab
4. Delete any existing policies
5. Run this SQL in SQL Editor:

```sql
ALTER TABLE guests ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public insert" ON guests
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read" ON guests
    FOR SELECT USING (true);
```

6. Restart Flask app

---

### Error 3: "Could not find the table" or "PGRST205"
```
ERROR: Could not find the table 'public.guests' in the schema cache
```

**Fix**: Same as Error 1 - the table doesn't exist

Run the SQL from `GUESTS_TABLE.sql` in Supabase SQL Editor.

---

### Error 4: "Connection refused" or Database connection error
```
ERROR: Connection refused to Supabase
```

**Fix**: Check your Supabase credentials

1. Open your `.env` file
2. Verify these are set:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key-here
   ```
3. Get the correct values from: https://app.supabase.com/ → Settings → API
4. Save `.env`
5. Restart Flask app

---

### Error 5: Response data is empty
```
⚠️ Response data is empty
```

**Fix**: The insert succeeded but response is malformed

This might be an RLS policy issue. Try:

```sql
-- Test that you can insert
INSERT INTO guests (name, email) VALUES ('Test', 'test@example.com');

-- If that fails, check RLS policies
-- Try the Error 2 fix above
```

---

## Step-by-Step Diagnosis

### 1. Verify Table Exists
In Supabase SQL Editor, run:
```sql
\dt guests
```

Should show table details. If nothing shows, table doesn't exist.

### 2. Verify Permissions
Run in SQL Editor:
```sql
SELECT * FROM guests;
```

If this fails with "permission denied", you have RLS policy issues.

### 3. Test Insert Directly
In SQL Editor:
```sql
INSERT INTO guests (name, email) VALUES ('Test Guest', 'test@example.com')
RETURNING *;
```

This should succeed and show the inserted row. If it fails, you've found the issue.

### 4. Check Supabase Credentials
In your Flask app terminal, check if Supabase is connecting:

```python
from database.supabase_client import supabase
print(supabase.auth.get_user())
```

Should show authentication status.

---

## What to Look For in Terminal

After restarting Flask and trying guest registration, watch for these signs:

### ✅ SUCCESS:
```
🔵 Guest registration attempt:
   Name: [your name]
✅ Guest record created successfully!
```

### ❌ TABLE MISSING:
```
❌ DATABASE ERROR: Guests table not found
❌ ERROR creating guest record: relation "guests" does not exist
```
→ Run SQL from GUESTS_TABLE.sql

### ❌ PERMISSION ISSUE:
```
❌ ERROR creating guest record: permission denied
❌ ERROR creating guest record: violates row level security policy
```
→ Fix RLS policies (Error 2 above)

### ❌ CONNECTION ISSUE:
```
❌ ERROR creating guest record: Connection refused
❌ ERROR creating guest record: Could not find Supabase credentials
```
→ Check .env file and SUPABASE_URL/SUPABASE_KEY

---

## Complete Recovery Steps

If nothing above works, try this complete reset:

### 1. Stop Flask (Ctrl+C)

### 2. In Supabase SQL Editor, run:
```sql
-- Drop and recreate the table
DROP TABLE IF EXISTS guests CASCADE;

CREATE TABLE guests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_guests_email ON guests(email);
CREATE INDEX idx_guests_created_at ON guests(created_at);

ALTER TABLE guests ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public insert" ON guests
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read" ON guests
    FOR SELECT USING (true);
```

### 3. Test the table:
```sql
INSERT INTO guests (name, email) VALUES ('Test', 'test@example.com');
SELECT * FROM guests;
```

### 4. Restart Flask:
```powershell
python app.py
```

### 5. Try guest registration again

---

## Still Not Working?

1. **Copy the entire terminal output** (all error messages)
2. **Take a screenshot** of the Supabase SQL Editor showing:
   - The guests table in Table Editor
   - The Policies tab
3. **Check your .env file** for:
   - SUPABASE_URL is set
   - SUPABASE_KEY is set
4. **Share these with support** for further diagnosis

---

## Quick Checklist

- [ ] Flask app is running
- [ ] Terminal shows no "connection refused" errors
- [ ] guests table exists in Supabase
- [ ] RLS policies are configured
- [ ] SUPABASE_URL and SUPABASE_KEY are set in .env
- [ ] Flask app was restarted after making changes
- [ ] Browser cache was cleared (Ctrl+Shift+Del)
- [ ] You're using the same Supabase project as before

