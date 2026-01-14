# Launch Guide - Wipeout & Chill 🏄‍♂️

**Surfing for the Rest of Us!**

Welcome to Wipeout & Chill - where we get it. You didn't grow up on a board. Neither did we. But that doesn't mean you can't have fun!

## Prerequisites Checklist

Before launching, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] Supabase account with PostgreSQL database
- [ ] Supabase Auth enabled
- [ ] Database connection credentials
- [ ] Supabase project URL and anon key

## Step-by-Step Launch Instructions

### 1. Install Dependencies

```bash
# Navigate to project directory
cd /Users/mark.karels/Documents/GitHub/2026_nCino_AI_Project

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install all dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create or update your `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production

# Database Connection (choose one method)
# Method 1: Full connection string
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.odeeytgzxqebjnpwqkzp.supabase.co:5432/postgres

# Method 2: Individual parameters (if DATABASE_URL not set)
user=postgres
password=your-supabase-password
host=db.odeeytgzxqebjnpwqkzp.supabase.co
port=5432
dbname=postgres

# Supabase Auth (REQUIRED)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Email Configuration (Optional - for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

**Where to find Supabase credentials:**
1. Go to your Supabase project dashboard
2. Settings → API → Project URL = `SUPABASE_URL`
3. Settings → API → anon/public key = `SUPABASE_ANON_KEY`
4. Settings → Database → Connection string = `DATABASE_URL` (or use individual params)

### 3. Set Up Database Schema

Run the migration script to create all tables:

**Option A: Using Supabase SQL Editor (Recommended)**
1. Go to Supabase Dashboard → SQL Editor
2. Click "New Query"
3. Copy and paste the entire contents of `migrations/001_initial_schema.sql`
4. Click "Run" to execute

**Option B: Using psql command line**
```bash
psql -h db.odeeytgzxqebjnpwqkzp.supabase.co -U postgres -d postgres -f migrations/001_initial_schema.sql
```

### 4. Test Database Connection

```bash
python scripts/test_db_connection.py
```

You should see:
```
✓ Connection successful!
✓ Query execution successful!
✓ Connection pool working correctly!
```

### 5. Create Initial Data (Optional but Recommended)

**Create a Location:**
```sql
INSERT INTO locations (name, timezone, address) 
VALUES ('Lake Shore Location', 'America/Chicago', '123 Lake Shore Drive, Chicago, IL');
```

**Add Sample Boards with Fun Names:**
Run the sample data migration:
```sql
-- In Supabase SQL Editor, run:
migrations/002_sample_data.sql
```

This will create:
- A Chicago-inspired location
- 10 fun, beginner-friendly boards with names like:
  - "The Windy City Wipeout"
  - "Da Bears Board"
  - "Lake Michigan Dreamer"
  - "The Fall Classic"
  - "Movie Night Special"
  - And more!

**Note the location ID** (you'll need it for registration, or it will be in the dropdown)

### 6. Launch the Application

```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

### 7. Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

## First-Time Setup

### 1. Register Your First User

1. Click "Register" on the login page
2. Fill in:
   - Full Name
   - Email
   - Password
   - Select Location (from dropdown)
3. Click "Register"

**Note:** The first user will be a regular user. To make them an admin:

```sql
UPDATE users SET role = 'admin' WHERE email = 'your-email@example.com';
```

### 2. Add Boards (Admin Only)

**Option A: Use Sample Data (Recommended)**
Run `migrations/002_sample_data.sql` to get fun, beginner-friendly boards with names like:
- "The Windy City Wipeout"
- "Da Bears Board" 
- "Lake Michigan Dreamer"
- "The Fall Classic"
- "Movie Night Special"
- And more!

**Option B: Add Custom Boards**
Once logged in as admin, you can add boards via SQL:

```sql
INSERT INTO boards (location_id, name, brand, size, status, condition)
SELECT 
    id,
    'Your Board Name',
    'Brand Name',
    '9''0',
    'available',
    'excellent'
FROM locations 
WHERE name = 'Lake Shore Location'
LIMIT 1;
```

## Testing the Application

### Test User Flow

1. **Login/Register**
   - ✅ Register a new user
   - ✅ Login with credentials
   - ✅ Verify redirect to dashboard

2. **View Available Boards**
   - ✅ Navigate to "Boards"
   - ✅ See list of available boards
   - ✅ Search/filter boards

3. **Checkout a Board**
   - ✅ Click "Checkout" on an available board
   - ✅ Verify board disappears from available list
   - ✅ Check "My Checkouts" to see active checkout
   - ✅ Verify expected return time is calculated correctly

4. **Return a Board**
   - ✅ Go to "My Checkouts"
   - ✅ Click "Return" on active checkout
   - ✅ Verify board appears back in available list
   - ✅ Test damage reporting (optional)

5. **Reservations**
   - ✅ View a checked-out board
   - ✅ Click "Reserve" (should be available after return time)
   - ✅ Check "My Reservations" to see pending reservation

### Test Admin Flow

1. **Admin Dashboard**
   - ✅ View stats (available, checked out, damaged counts)
   - ✅ See recent checkouts
   - ✅ See new damage reports

2. **Inventory Management**
   - ✅ View all boards
   - ✅ Search/filter boards
   - ✅ See board statuses

3. **Damage Queue**
   - ✅ View damage reports
   - ✅ Update damage status (New → In Repair → Replaced)
   - ✅ Filter by status

4. **Activity Log**
   - ✅ View all system activities
   - ✅ See timestamps and action details

5. **Reports**
   - ✅ View favorite boards
   - ✅ View usage per user
   - ✅ See usage trends chart
   - ✅ View seasonal trends
   - ✅ See peak usage times

## Troubleshooting

### Database Connection Issues

**Error: "Database configuration missing"**
- Check `.env` file exists and has correct credentials
- Verify DATABASE_URL or individual DB parameters are set

**Error: "Connection refused"**
- Verify Supabase database is running
- Check firewall/network settings
- Verify connection string format

### Authentication Issues

**Error: "Supabase not configured"**
- Check `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`
- Verify Supabase Auth is enabled in your project

**Error: "User not found in database"**
- User was created in Supabase Auth but not in your database
- Check if user record exists: `SELECT * FROM users WHERE email = 'your-email';`

### WebSocket/Real-Time Issues

**Connection indicator shows "Connecting..."**
- Check browser console for errors
- Verify Flask-SocketIO is installed: `pip list | grep Flask-SocketIO`
- Check server logs for WebSocket errors

### Template Errors

**Error: "Template not found"**
- Verify all template files exist in `templates/` directory
- Check file names match route template names exactly

## Common Issues & Solutions

### Issue: "No boards available"
**Solution:** Add boards to database (see "Add Boards" section above)

### Issue: "Can't register - no locations"
**Solution:** Create a location first:
```sql
INSERT INTO locations (name, timezone, address) 
VALUES ('Your Location', 'America/Los_Angeles', 'Your Address');
```

### Issue: "Permission denied" errors
**Solution:** 
- Verify user has correct role: `SELECT role FROM users WHERE id = 'user-id';`
- Check location_id matches user's location

### Issue: Charts not displaying in reports
**Solution:**
- Check browser console for JavaScript errors
- Verify Chart.js CDN is loading (check network tab)
- Ensure data is being passed to template correctly

## Development Tips

### Enable Debug Mode
Already enabled in `app.py`:
```python
app.run(debug=True, ...)
```

### View Logs
Check terminal output for:
- Database queries
- Authentication attempts
- WebSocket connections
- Error messages

### Test Real-Time Updates
1. Open application in two browser windows
2. Checkout a board in one window
3. Verify board disappears in the other window (real-time update)

## Next Steps After Launch

1. **Add More Boards:** Use SQL or create admin form
2. **Test All Features:** Go through acceptance criteria checklist
3. **Customize UI:** Adjust colors, styling in `static/css/custom.css`
4. **Add Email Notifications:** Configure SMTP settings
5. **Deploy:** When ready, deploy to production server

## Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review server logs in terminal
3. Check browser console for JavaScript errors
4. Verify all environment variables are set correctly
5. Ensure database schema is fully migrated

---

**Ready to launch!** 🚀

Run `python app.py` and navigate to `http://localhost:5000`
