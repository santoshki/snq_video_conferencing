# 🚀 Guest Registration System - Setup Complete

## Issue You're Experiencing
```
Error: "relation 'guests' does not exist" (42P01)
```

**Cause**: The `guests` database table hasn't been created in your Supabase project yet.

---

## ✅ Step-by-Step Fix (Easy - Just Copy & Paste)

### Step 1: Open Supabase SQL Editor
```
Go to → https://app.supabase.com/
  ├─ Select your project
  ├─ Click "SQL Editor" (left sidebar)
  └─ Click "New Query"
```

### Step 2: Copy This SQL (The Entire Block)
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

### Step 3: Paste Into SQL Editor
- Click in the text area
- Press Ctrl+V (or Cmd+V)
- Paste the SQL above

### Step 4: Run The Query
- Click the blue "Run" button at bottom right
- Wait for success message ✓

You should see:
```
✓ CREATE TABLE
✓ CREATE INDEX
✓ CREATE INDEX
✓ ALTER TABLE
✓ CREATE POLICY
✓ CREATE POLICY
```

### Step 5: Verify Success
Run this query to confirm:
```sql
SELECT COUNT(*) as guest_count FROM guests;
```

Should return: `guest_count: 0` (empty table is fine)

### Step 6: Restart Your Flask App
```powershell
# Stop the app if running (Ctrl+C)
# Then restart:
python app.py
```

---

## 🧪 Test the Guest Registration

1. **Open browser**: http://localhost:5000

2. **Don't log in** - just close the login page

3. **Try joining a meeting**:
   - Go directly to: http://localhost:5000/meeting/test-room-123
   - You should be redirected to guest registration form

4. **Register as guest**:
   - Enter your name (required)
   - Optionally enter email
   - Click "Join Meeting"

5. **Success!** 🎉
   - You should see the meeting room
   - Your name appears in participant list

---

## 📁 What Changed In Your Code

### New Files:
- ✅ `/database/create_guest.py` - Guest database operations
- ✅ `/templates/guest_register.html` - Registration form UI
- ✅ `/database/__init__.py` - Python package setup
- ✅ `/database/verify_db.py` - Database verification tool
- ✅ `/database/init_db.py` - Database initialization helper

### Modified Files:
- ✅ `/app.py` - Added guest registration route & modified meeting access

### Documentation:
- ✅ `/GUEST_REGISTRATION_CHANGES.md` - Technical details
- ✅ `/FIX_GUESTS_TABLE.md` - Database setup guide
- ✅ `/SUPABASE_SETUP.md` - Additional setup reference

---

## 🔄 User Journey

### Before (Broken):
```
Unauthenticated User
  ↓
Directly joins meeting as "Guest"
  ↓
No registration needed ❌
```

### After (Fixed):
```
Unauthenticated User
  ↓
Tries to access /meeting/<room_id>
  ↓
Redirected to /guest_register/<room_id>
  ↓
Fills out guest form (name required)
  ↓
Database record created ✅
  ↓
Joins meeting as Registered Guest ✅
```

---

## 🆘 Troubleshooting

### Still Getting Error?
- [ ] Did you run ALL the SQL (not just first 3 lines)?
- [ ] Did you click "Run" button?
- [ ] Did you wait for it to complete?
- [ ] Did you restart the Flask app?
- [ ] Are you in the correct Supabase project?

### Quick Verification in Supabase:
```sql
-- Check if table exists
\dt guests

-- See table structure
\d guests

-- Count guests
SELECT COUNT(*) FROM guests;
```

### Need to Delete & Recreate?
```sql
-- Delete the table (WARNING: Deletes all guest records)
DROP TABLE IF EXISTS guests CASCADE;

-- Then run the full SQL from Step 2 above
```

---

## 📚 Additional Resources

- **Supabase Docs**: https://supabase.com/docs
- **RLS Policies**: https://supabase.com/docs/guides/auth/row-level-security
- **SQL Editor Help**: https://supabase.com/docs/guides/database/sql-editor

---

## ✨ Next Steps

After setup is complete:

1. **Test thoroughly** with both logged-in users and guests
2. **Monitor logs** for any errors in terminal
3. **Consider adding** guest session timeout (optional)
4. **Add analytics** to track guest participation (optional)
5. **Set up backups** for guest data in Supabase

---

## 🎯 Summary

| Item | Status | Notes |
|------|--------|-------|
| Code Changes | ✅ Done | Guest registration system implemented |
| Database Table | ⏳ Needs Setup | Run SQL from Step 2 above |
| Testing | 🔄 Ready | Test after table creation |
| Production Ready | ⏳ Pending | After testing & verification |

**Once you run the SQL in Supabase, everything will work!** 🚀

