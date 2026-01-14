# Database Setup Guide - Create Tables in Supabase

## Quick Answer

**You need to run the migration SQL script in your Supabase SQL Editor to create the tables.**

We created the SQL files (`migrations/001_initial_schema.sql`) but haven't executed them against your database yet. Here's how to do it:

## Method 1: Using Supabase SQL Editor (Easiest - Recommended)

1. **Go to your Supabase Dashboard**
   - Navigate to: https://supabase.com/dashboard
   - Select your project: **"2026_nCino_AI_Project"**

2. **Open SQL Editor**
   - Click on **"SQL Editor"** in the left sidebar
   - Click **"New Query"** button

3. **Copy the Migration Script**
   - Open the file: `migrations/001_initial_schema.sql`
   - Copy **ALL** the contents (Ctrl+A, Ctrl+C / Cmd+A, Cmd+C)

4. **Paste and Run**
   - Paste the SQL into the Supabase SQL Editor
   - Click **"Run"** button (or press Ctrl+Enter / Cmd+Enter)

5. **Verify Tables Were Created**
   - Go to **"Table Editor"** in the left sidebar
   - You should now see 8 tables:
     - `locations`
     - `users`
     - `boards`
     - `checkouts`
     - `reservations`
     - `damage_reports`
     - `activity_log`
     - `board_ratings`

## Method 2: Using psql Command Line

If you have `psql` installed and prefer command line:

```bash
# Get your connection string from Supabase Dashboard
# Settings → Database → Connection string

psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres" -f migrations/001_initial_schema.sql
```

Replace:
- `[YOUR-PASSWORD]` with your Supabase database password
- `[YOUR-PROJECT-REF]` with your project reference ID

## Method 3: Using Python Script (Alternative)

You can also run it via Python if you prefer:

```python
# run_migration.py
from database import db
import os

def run_migration():
    with open('migrations/001_initial_schema.sql', 'r') as f:
        sql = f.read()
    
    # Split by semicolons and execute each statement
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    
    for statement in statements:
        try:
            db.execute_query(statement)
            print(f"✓ Executed: {statement[:50]}...")
        except Exception as e:
            print(f"✗ Error: {e}")
            print(f"  Statement: {statement[:100]}...")

if __name__ == '__main__':
    run_migration()
    print("\n✓ Migration complete! Check your Supabase dashboard for tables.")
```

## After Running Migration

### 1. Add Sample Data (Optional but Recommended)

After creating the tables, you can add sample data:

1. In Supabase SQL Editor, open `migrations/002_sample_data.sql`
2. **IMPORTANT:** First, you need to get your location ID:
   ```sql
   -- Run this first to create a location and get its ID
   INSERT INTO locations (name, timezone, address) 
   VALUES ('Lake Shore Location', 'America/Chicago', '123 Lake Shore Drive, Chicago, IL')
   RETURNING id;
   ```
3. Copy the location ID that's returned
4. In `002_sample_data.sql`, replace `YOUR_LOCATION_ID` with the actual UUID
5. Run the sample data script

### 2. Verify Everything Works

Test your database connection:

```bash
python scripts/test_db_connection.py
```

You should see:
```
✓ Connection successful!
✓ Query execution successful!
✓ Connection pool working correctly!
```

## Troubleshooting

### "relation already exists" errors
- This means some tables already exist. You can either:
  - Drop existing tables first (if safe to do so)
  - Or modify the migration to use `CREATE TABLE IF NOT EXISTS` (which it already does)

### "permission denied" errors
- Make sure you're using the correct database user (usually `postgres`)
- Check your connection string has the right password

### "extension uuid-ossp does not exist"
- Supabase should have this enabled by default, but if not:
  ```sql
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
  ```

## What Gets Created

The migration creates:

1. **8 Tables:**
   - `locations` - Surfboard rental locations
   - `users` - User accounts (linked to Supabase Auth)
   - `boards` - Surfboards inventory
   - `checkouts` - Board checkout records
   - `reservations` - Board reservations
   - `damage_reports` - Damage reporting
   - `activity_log` - Audit trail
   - `board_ratings` - Board ratings (bonus feature)

2. **Indexes** for performance
3. **Foreign Keys** for data integrity
4. **Constraints** for data validation

## Next Steps

Once tables are created:
1. ✅ Tables visible in Supabase Table Editor
2. ✅ Run sample data script (optional)
3. ✅ Test connection: `python scripts/test_db_connection.py`
4. ✅ Launch app: `python app.py`
5. ✅ Register first user
6. ✅ Make user admin (via SQL or app)

---

**Remember:** The migration script uses `CREATE TABLE IF NOT EXISTS`, so it's safe to run multiple times - it won't break if tables already exist!
