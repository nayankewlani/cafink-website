# CAFLink – Full Stack Website

A complete, production-ready website for CAFLink Digital Agency.

## Stack
| Layer      | Technology                      |
|------------|--------------------------------|
| Frontend   | HTML5, CSS3, Vanilla JS        |
| Backend    | Python 3 + Flask               |
| Database   | SQLite (via Python sqlite3)    |
| Fonts      | Google Fonts (Syne + DM Sans)  |

---

## Project Structure
```
caflink_project/
├── app.py                  ← Flask backend (all routes & API)
├── db/
│   └── caflink.db          ← SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css       ← Full stylesheet (white theme)
│   └── js/
│       └── main.js         ← Frontend logic, API calls
└── templates/
    └── index.html          ← Main Jinja2 template
```

---

## Setup & Run

### Requirements
- Python 3.7+
- Flask (`pip install flask`)

### Steps
```bash
# 1. Navigate to project
cd caflink_project

# 2. Install Flask (if not installed)
pip install flask

# 3. Run the server
python app.py

# 4. Open browser
# http://localhost:5000
```

---

## API Endpoints

| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| GET    | `/`                       | Main website                       |
| GET    | `/api/services`           | Fetch all active services          |
| GET    | `/api/testimonials`       | Fetch approved testimonials        |
| GET    | `/api/stats`              | Fetch hero statistics              |
| POST   | `/api/contact`            | Submit contact form                |
| POST   | `/api/newsletter`         | Subscribe to newsletter            |
| GET    | `/api/admin/contacts`     | View all contact submissions       |
| GET    | `/api/admin/subscribers`  | View all newsletter subscribers    |

---

## Database Schema

### contacts
| Column     | Type      | Notes                   |
|------------|-----------|-------------------------|
| id         | INTEGER   | Primary key             |
| first_name | TEXT      | Required                |
| last_name  | TEXT      |                         |
| email      | TEXT      | Required, validated     |
| phone      | TEXT      |                         |
| service    | TEXT      | Required                |
| budget     | TEXT      |                         |
| message    | TEXT      |                         |
| created_at | TIMESTAMP | Auto                    |
| status     | TEXT      | 'new' / 'done'          |

### newsletter
| Column        | Type      | Notes           |
|---------------|-----------|-----------------|
| id            | INTEGER   | Primary key     |
| email         | TEXT      | Unique          |
| subscribed_at | TIMESTAMP | Auto            |
| active        | INTEGER   | 1 = active      |

### services / testimonials / stats
See `app.py` → `init_db()` for full schema.

---

## Features
- ✅ White-themed professional design
- ✅ Navbar: Home | About Us | Services | Contact Us
- ✅ Notification bar (auto-shows, dismissible)
- ✅ Services loaded from database via API
- ✅ Testimonials loaded from database via API
- ✅ Contact form with server-side validation & DB storage
- ✅ Newsletter subscription with DB storage
- ✅ Scroll-reveal animations
- ✅ Animated counters
- ✅ Responsive mobile menu
- ✅ Toast notifications
- ✅ Scroll-to-top button
- ✅ Admin API endpoints for viewing submissions
