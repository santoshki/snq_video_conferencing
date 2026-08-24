# ✅ Setup Verification Checklist

## Pre-Setup Check
- [ ] You have access to Supabase dashboard
- [ ] You can access your project in Supabase
- [ ] You have Python 3.x and Flask running locally
- [ ] You can access http://localhost:5000

## Database Setup
- [ ] Opened Supabase SQL Editor
- [ ] Created new query in Supabase
- [ ] Copied all SQL from `GUESTS_TABLE.sql`
- [ ] Pasted SQL into Supabase editor
- [ ] Clicked Run button
- [ ] Saw success messages (6 checkmarks):
  - [ ] ✓ CREATE TABLE
  - [ ] ✓ CREATE INDEX (first)
  - [ ] ✓ CREATE INDEX (second)
  - [ ] ✓ ALTER TABLE
  - [ ] ✓ CREATE POLICY (first)
  - [ ] ✓ CREATE POLICY (second)

## Verification Queries (Optional)
Run these in Supabase to confirm setup:

**Query 1: Check table exists**
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'guests';
```
Expected result: One row with `guests`

**Query 2: Check table is empty**
```sql
SELECT COUNT(*) as guest_count FROM guests;
```
Expected result: `0`

- [ ] Query 1 passed ✓
- [ ] Query 2 passed ✓

## Application Setup
- [ ] Restarted Flask app (`python app.py`)
- [ ] Flask is running without errors
- [ ] No error messages in terminal about "guests" table

## Functionality Test
- [ ] Can access http://localhost:5000
- [ ] Login page loads correctly
- [ ] Can navigate without logging in
- [ ] Visit: http://localhost:5000/meeting/test-meet-123
- [ ] **REDIRECTED** to guest registration form ✅
- [ ] Guest registration form displays:
  - [ ] Meeting ID shown
  - [ ] Name field is present (required)
  - [ ] Email field is present (optional)
  - [ ] Join Meeting button visible
- [ ] Can enter guest name
- [ ] Can submit guest registration
- [ ] Successfully enter meeting room ✅
- [ ] Your guest name appears in meeting

## In Supabase After Testing
```sql
-- Check if your guest was recorded
SELECT * FROM guests ORDER BY created_at DESC LIMIT 1;
```
- [ ] Your guest name appears in database ✓
- [ ] Email recorded (if you entered one)
- [ ] Timestamp is recent

## Troubleshooting

### If you get "guests table not found" error
- [ ] Verify you ran ALL SQL (check for 6 success messages)
- [ ] Verify you're using correct Supabase project
- [ ] Try refreshing Supabase page
- [ ] Stop and restart Flask app
- [ ] Clear browser cache (Ctrl+Shift+Del)

### If guest registration form doesn't appear
- [ ] Verify you're not logged in
- [ ] Check browser console for errors (F12)
- [ ] Check terminal for Flask errors
- [ ] Verify `/guest_register/<room_id>` endpoint works

### If can't submit guest form
- [ ] Check Flask terminal for errors
- [ ] Verify database credentials in `.env`
- [ ] Verify Supabase table permissions (RLS policies)
- [ ] Check database connection

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "relation does not exist" | Run all SQL from GUESTS_TABLE.sql |
| "Permission denied" | Check RLS policies in Supabase |
| Redirect loop | Verify session is being saved in Flask |
| Form won't submit | Check browser console (F12) for errors |
| Guest doesn't appear | Verify database connection & table exists |

## Final Status

Once all checkboxes are complete:

```
✅ Database setup complete
✅ Application updated
✅ Guest registration working
✅ Guests saved to database
✅ System ready for production
```

---

## Still Having Issues?

1. Read `SETUP_GUIDE.md` for detailed instructions
2. Check `FIX_GUESTS_TABLE.md` for database setup help
3. Review error messages in Flask terminal
4. Run: `python database/verify_db.py` to check connection
5. Check Supabase dashboard for table and data

---

**Date Completed**: ________________
**All Tests Passed**: [ ] Yes  [ ] No
**Notes**: _________________________________________________________________

