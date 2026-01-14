# 🏄‍♂️ Wipeout & Chill

**Surfing for the Rest of Us!**

A quirky, beginner-friendly surfboard checkout system built with Flask, Supabase, and a whole lot of personality. We get it - you didn't grow up on a board. Neither did we. But that doesn't mean you can't have fun!

## About

Wipeout & Chill is a multi-location surfboard checkout and inventory management system designed for people who are learning to surf. It's built with:

- **Flask 3.0** - Python web framework
- **Supabase** - PostgreSQL database + Auth
- **Bootstrap 5** - Modern, responsive UI
- **Flask-SocketIO** - Real-time updates
- **A sense of humor** - Because falling is part of the fun!

## Features

✅ **Beginner-Friendly Checkout System** - Check out boards, return them, report damage  
✅ **Reservation System** - Reserve boards for when they become available  
✅ **Real-Time Updates** - See board availability change in real-time  
✅ **Admin Portal** - Manage inventory, damage reports, and view analytics  
✅ **Timezone-Aware** - Return windows calculated based on location timezone  
✅ **Multi-Tenancy** - Each location manages their own boards  
✅ **Reporting & Analytics** - See favorite boards, usage trends, and more  
✅ **Personality** - Fun, encouraging messages throughout  

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Add your Supabase credentials

3. **Set up database:**
   - Run `migrations/001_initial_schema.sql` in Supabase SQL Editor
   - Run `migrations/002_sample_data.sql` for fun sample data

4. **Launch:**
   ```bash
   python app.py
   ```

5. **Visit:**
   ```
   http://localhost:5000
   ```

For detailed setup instructions, see [docs/LAUNCH_GUIDE.md](docs/LAUNCH_GUIDE.md)

## Project Structure

```
2026_nCino_AI_Project/
├── models/          # Data models (OOP classes)
├── services/        # Business logic layer
├── routes/          # Flask blueprints
├── templates/       # Jinja2 templates
├── static/          # CSS, JavaScript, images
├── utils/           # Utilities, constants, branding
└── migrations/      # Database migration scripts
```

## The Brand

**Wipeout & Chill** embraces the beginner surfer experience:
- Encouraging but realistic
- Fun and quirky
- No judgment, just good vibes
- Subtle nods to Chicago, Bears, movies, and Fall

## Philosophy

> "The best surfer is the one having the most fun. That's you!"

We believe:
- Falling is learning
- Progress, not perfection
- Every wipeout is a story
- You're not bad at surfing, you're just new at it

## Tech Stack

- **Backend:** Flask, Flask-Login, Flask-SocketIO
- **Database:** Supabase PostgreSQL
- **Auth:** Supabase Auth
- **Frontend:** Bootstrap 5, JavaScript, Chart.js
- **Real-Time:** WebSocket (Socket.IO)

## License

Built for the nCino AI-Assisted Development Hackathon 2026

---

**Remember: Every pro was once a beginner who didn't give up!** 🏄‍♂️
