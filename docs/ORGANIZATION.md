# Project Organization

This document explains the project structure and where to find things.

## Directory Structure

```
2026_nCino_AI_Project/
├── app.py                    # Main Flask application
├── config.py                 # Configuration
├── database.py              # Database connection
├── requirements.txt         # Python dependencies
├── README.md                # Project overview
├── PROJECT_PLAN.md          # Original project plan
├── nCino_Surfboard_Checkout_Project_Requirements.md  # Original requirements
│
├── docs/                    # 📚 Documentation
│   ├── LAUNCH_GUIDE.md      # How to launch and test
│   ├── SETUP.md             # Initial setup instructions
│   ├── DATABASE_SETUP.md   # Database setup guide
│   ├── PROJECT_PLAN_VERIFICATION.md  # What's been built
│   ├── FINAL_CHECKLIST.md   # Pre-launch checklist
│   ├── REQUIREMENTS_REVIEW.md  # Requirements coverage
│   ├── REVIEW_SUMMARY.md    # Summary of review
│   ├── VERIFICATION_REPORT.md  # Verification details
│   └── PROJECT_STATUS.md    # Status tracking
│
├── scripts/                 # 🔧 Utility Scripts
│   ├── run_migrations.py   # Run database migrations
│   ├── test_db_connection.py  # Test database connection
│   └── test_supabase_connection.py  # Test Supabase connection
│
├── migrations/              # 🗄️ Database Migrations
│   ├── 001_initial_schema.sql  # Create all tables
│   └── 002_sample_data.sql     # Sample data
│
├── models/                  # 📦 Data Models (OOP)
│   ├── location.py
│   ├── user.py
│   ├── board.py
│   ├── checkout.py
│   ├── reservation.py
│   ├── damage_report.py
│   ├── activity_log.py
│   └── board_rating.py
│
├── services/                # 🧠 Business Logic (OOP)
│   ├── auth_service.py
│   ├── checkout_service.py
│   ├── reservation_service.py
│   ├── notification_service.py
│   ├── timezone_service.py
│   └── reporting_service.py
│
├── routes/                  # 🛣️ Flask Routes (Blueprints)
│   ├── auth_routes.py
│   ├── user_routes.py
│   ├── admin_routes.py
│   └── api_routes.py
│
├── templates/              # 🎨 HTML Templates (Jinja2)
│   ├── base.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── user/
│   │   ├── dashboard.html
│   │   ├── boards.html
│   │   ├── my_checkouts.html
│   │   └── reservations.html
│   └── admin/
│       ├── dashboard.html
│       ├── inventory.html
│       ├── checkout_schedule.html
│       ├── damage_queue.html
│       ├── activity_log.html
│       └── reports.html
│
├── static/                 # 🎨 Static Assets
│   ├── css/
│   │   ├── custom.css
│   │   ├── animations.css
│   │   └── branding.css
│   ├── js/
│   │   ├── main.js
│   │   ├── socketio_client.js
│   │   ├── checkout_handler.js
│   │   ├── user_dashboard.js
│   │   └── admin_dashboard.js
│   └── img/
│
└── utils/                  # 🛠️ Utilities
    ├── constants.py        # All repeated strings
    ├── branding.py         # Branding/personality
    └── decorators.py       # Auth decorators
```

## Quick Reference

### Where to Find Things

**Documentation:**
- Setup instructions → `docs/SETUP.md`
- Launch guide → `docs/LAUNCH_GUIDE.md`
- Database setup → `docs/DATABASE_SETUP.md`
- What's been built → `docs/PROJECT_PLAN_VERIFICATION.md`

**Scripts:**
- Run migrations → `python scripts/run_migrations.py`
- Test connection → `python scripts/test_db_connection.py`

**Code:**
- Models → `models/` (one class per file)
- Business logic → `services/` (one service per file)
- Routes → `routes/` (grouped by user type)
- Templates → `templates/` (mirrors route structure)

**Configuration:**
- App config → `config.py`
- Database config → `.env` file
- Constants → `utils/constants.py`
- Branding → `utils/branding.py`

## File Organization Principles

1. **Clear Names:** Every file name indicates its purpose
2. **Single Responsibility:** Each file has one clear purpose
3. **Small Files:** No file exceeds ~300 lines
4. **OOP First:** Classes for models, services, utilities
5. **Easy Navigation:** Structure mirrors feature domains

## Making Changes

**To add a new feature:**
1. Add model → `models/`
2. Add service → `services/`
3. Add route → `routes/`
4. Add template → `templates/`
5. Add JS → `static/js/`

**To update constants:**
- Edit `utils/constants.py` or `utils/branding.py`

**To run migrations:**
- Use `scripts/run_migrations.py` or run SQL in Supabase

**To test:**
- Use `scripts/test_db_connection.py`
