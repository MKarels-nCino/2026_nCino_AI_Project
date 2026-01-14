# Setup Guide - nCino Surfboard Checkout System

## Prerequisites

- Python 3.8+
- Supabase account with PostgreSQL database
- Supabase Auth configured

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

Run the migration script to create all tables:

```bash
# Connect to your Supabase database and run:
psql -h db.odeeytgzxqebjnpwqkzp.supabase.co -U postgres -d postgres -f migrations/001_initial_schema.sql
```

Or use your Supabase SQL editor to run the migration script.

### 3. Environment Variables

Ensure your `.env` file contains:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.odeeytgzxqebjnpwqkzp.supabase.co:5432/postgres

# Or individual parameters:
user=postgres
password=your-password
host=db.odeeytgzxqebjnpwqkzp.supabase.co
port=5432
dbname=postgres

# Supabase Auth (required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Email (optional - for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### 4. Test Database Connection

```bash
python scripts/test_db_connection.py
```

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Initial Setup

1. **Create Locations**: You'll need to create at least one location in the database:
   ```sql
   INSERT INTO locations (name, timezone, address) 
   VALUES ('San Diego', 'America/Los_Angeles', '123 Beach St, San Diego, CA');
   ```

2. **Register First User**: Use the registration page to create your first user account.

3. **Create Admin User**: Update a user to admin role:
   ```sql
   UPDATE users SET role = 'admin' WHERE email = 'your-email@example.com';
   ```

4. **Add Boards**: Use the admin portal to add surfboards to your location.

## Project Structure

- `models/` - Data models (OOP classes)
- `services/` - Business logic layer
- `routes/` - Flask blueprints (HTTP handlers)
- `templates/` - Jinja2 templates
- `static/` - CSS, JavaScript, images
- `utils/` - Utility functions and decorators
- `migrations/` - Database migration scripts

## Features Implemented

✅ User authentication (Supabase Auth)
✅ Board checkout/return system
✅ Timezone-aware return windows
✅ Reservation system
✅ Damage reporting
✅ Activity logging
✅ Admin portal
✅ Real-time updates (WebSocket)
✅ Multi-tenancy (location-based isolation)

## Next Steps

- Add more templates for admin features
- Enhance UI/UX with more animations
- Add email notification templates
- Implement advanced reporting visualizations
- Add board ratings UI
