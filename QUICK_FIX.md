# ⚡ QUICK FIX - 2 Minutes

## The Problem
```
ERROR: relation "guests" does not exist
```

## The Solution

### 1️⃣ Open Supabase
Go to: https://app.supabase.com/

### 2️⃣ Navigate to SQL Editor
- Select your project
- Click **SQL Editor** (left menu)
- Click **New Query**

### 3️⃣ Open This File
Open: `GUESTS_TABLE.sql` in your project folder

### 4️⃣ Copy All SQL
Select all text in `GUESTS_TABLE.sql` and copy (Ctrl+C)

### 5️⃣ Paste in Supabase
Paste (Ctrl+V) into the Supabase SQL Editor

### 6️⃣ Click Run
Click the blue "Run" button

### 7️⃣ See Green ✓
Wait for success messages (should see 6 checkmarks)

### 8️⃣ Restart App
```powershell
# In PowerShell, in your project directory:
# Press Ctrl+C to stop the app
# Then run:
python app.py
```

---

## Done! 🎉

Your guest registration system is now active.

- Unauthenticated users will be asked to register
- Guest names are stored in database
- Everything works as intended

---

## Test It
1. Go to http://localhost:5000
2. Don't login
3. Try joining a meeting: http://localhost:5000/meeting/test-123
4. Fill out guest registration form
5. You're in! ✅


