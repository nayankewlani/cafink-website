"""
CAFLink - Full Stack Web Application
Backend: Flask (Python)
Database: SQLite
"""

import sqlite3
import os
import re
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, g

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'db', 'caflink.db')
app.config['SECRET_KEY'] = 'caflink-secret-2025'

# ─────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database schema and seed data."""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    c = db.cursor()

    # ── contacts table ──
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            service TEXT,
            budget TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'new'
        )
    ''')

    # ── newsletter subscribers ──
    c.execute('''
        CREATE TABLE IF NOT EXISTS newsletter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1
        )
    ''')

    # ── testimonials ──
    c.execute('''
        CREATE TABLE IF NOT EXISTS testimonials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT,
            company TEXT,
            message TEXT NOT NULL,
            rating INTEGER DEFAULT 5,
            avatar TEXT,
            approved INTEGER DEFAULT 1
        )
    ''')

    # ── services ──
    c.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            features TEXT,
            active INTEGER DEFAULT 1
        )
    ''')

    # ── stats ──
    c.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL,
            value TEXT NOT NULL,
            suffix TEXT DEFAULT '+'
        )
    ''')

    # ── Seed testimonials ──
    c.execute("SELECT COUNT(*) FROM testimonials")
    if c.fetchone()[0] == 0:
        testimonials = [
            ("Rahul Kapoor", "CTO", "FinEdge Technologies",
             "CAFLink transformed our legacy system into a sleek, modern platform in under 3 months. The team was communicative, technically brilliant and delivered beyond expectations.", 5, "RK"),
            ("Priya Mehta", "Founder", "GrowthHive",
             "Their digital marketing campaign doubled our organic traffic in 60 days. The AI-driven content strategy they implemented was nothing short of game-changing for our startup.", 5, "PM"),
            ("Amit Sharma", "VP Engineering", "RetailPulse",
             "From database architecture to cloud hosting, CAFLink handled everything seamlessly. Our infrastructure costs dropped 40% while performance improved by 3x.", 5, "AS"),
            ("Sneha Verma", "CEO", "EduTech India",
             "Outstanding service delivery. CAFLink built our entire e-learning platform from scratch — beautifully designed, lightning fast, and on budget. Highly recommended!", 5, "SV"),
            ("Karan Joshi", "Product Head", "LogisticsPro",
             "The AI automation pipeline they built for us saves our team 20+ hours every week. Their technical depth and domain expertise is genuinely impressive.", 5, "KJ"),
            ("Meera Iyer", "Director", "HealthFirst",
             "CAFLink redesigned our patient portal and the engagement metrics went through the roof. Clean design, intuitive UX and zero downtime since launch.", 5, "MI"),
        ]
        c.executemany(
            "INSERT INTO testimonials (name, role, company, message, rating, avatar) VALUES (?,?,?,?,?,?)",
            testimonials
        )

    # ── Seed services ──
    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] == 0:
        services = [
            ("Software Development", "Custom software engineered for your exact workflows. Scalable architecture, clean code, continuous delivery.", "💻",
             '["Custom ERP/CRM Systems","API Development & Integration","Mobile Applications","Microservices Architecture","Code Review & Refactoring"]'),
            ("Web Development", "High-performance websites and web apps. React, Next.js, Node.js and more — fast, secure, beautiful.", "🌐",
             '["React / Next.js Frontends","Node.js & Python Backends","E-Commerce Platforms","Progressive Web Apps","UI/UX Design & Prototyping"]'),
            ("Database Management", "Architecture, optimization, migration and monitoring of your entire data layer — cloud or on-premise.", "🗄️",
             '["Database Design & Modeling","Query Optimization","Data Migration","Backup & Recovery","PostgreSQL / MongoDB / MySQL"]'),
            ("Server & Hosting", "Rock-solid cloud infrastructure with 99.9% uptime SLAs on AWS, GCP and Azure.", "☁️",
             '["Cloud Setup (AWS/GCP/Azure)","Docker & Kubernetes","CI/CD Pipelines","Auto-scaling & Load Balancing","24/7 Monitoring & Alerts"]'),
            ("Digital Marketing", "SEO, SEM, social media strategy and analytics dashboards that turn traffic into revenue.", "📈",
             '["Search Engine Optimization","Google Ads & PPC","Social Media Management","Email Campaigns","Conversion Rate Optimization"]'),
            ("Content Creation", "Brand-aligned content that resonates — blogs, video scripts, graphics and UI/UX assets.", "🎨",
             '["Brand Identity & Guidelines","Copywriting & Blogging","Infographics & Illustrations","Social Media Content","Video Production"]'),
            ("AI-Driven Platforms", "Custom AI integrations, LLM-powered workflows, automation pipelines and intelligent analytics.", "🤖",
             '["LLM Integration (GPT/Claude)","AI Chatbot Development","Predictive Analytics","Process Automation (RPA)","Computer Vision Solutions"]'),
        ]
        c.executemany(
            "INSERT INTO services (title, description, icon, features) VALUES (?,?,?,?)",
            services
        )

    # ── Seed stats ──
    c.execute("SELECT COUNT(*) FROM stats")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO stats (label, value, suffix) VALUES (?,?,?)",
            [("Projects Delivered","150","+"),("Client Satisfaction","98","%"),
             ("Years of Excellence","5","+"),("Expert Engineers","40","+")])

    db.commit()
    db.close()
    print("✅ Database initialized.")

# ─────────────────────────────────────────
# ROUTES – PAGES
# ─────────────────────────────────────────

@app.route('/')
def index():
    # Read base64-encoded images from file
    base_dir = os.path.dirname(__file__)
    def read_b64(path):
        try:
            with open(path, 'r') as f:
                return f.read().strip()
        except:
            return ''
    logo_b64    = read_b64(os.path.join(base_dir, '..', 'logo_b64.txt'))
    favicon_b64 = read_b64(os.path.join(base_dir, '..', 'favicon_b64.txt'))
    return render_template('index.html', logo_b64=logo_b64, favicon_b64=favicon_b64)

# ─────────────────────────────────────────
# API – SERVICES
# ─────────────────────────────────────────

@app.route('/api/services', methods=['GET'])
def get_services():
    db = get_db()
    rows = db.execute("SELECT * FROM services WHERE active=1").fetchall()
    result = []
    for r in rows:
        row = dict(r)
        row['features'] = json.loads(row['features']) if row['features'] else []
        result.append(row)
    return jsonify({"success": True, "data": result})

# ─────────────────────────────────────────
# API – TESTIMONIALS
# ─────────────────────────────────────────

@app.route('/api/testimonials', methods=['GET'])
def get_testimonials():
    db = get_db()
    rows = db.execute("SELECT * FROM testimonials WHERE approved=1").fetchall()
    return jsonify({"success": True, "data": [dict(r) for r in rows]})

# ─────────────────────────────────────────
# API – STATS
# ─────────────────────────────────────────

@app.route('/api/stats', methods=['GET'])
def get_stats():
    db = get_db()
    rows = db.execute("SELECT * FROM stats").fetchall()
    return jsonify({"success": True, "data": [dict(r) for r in rows]})

# ─────────────────────────────────────────
# API – CONTACT FORM
# ─────────────────────────────────────────

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    first_name = data.get('first_name', '').strip()
    last_name  = data.get('last_name', '').strip()
    email      = data.get('email', '').strip()
    phone      = data.get('phone', '').strip()
    service    = data.get('service', '').strip()
    budget     = data.get('budget', '').strip()
    message    = data.get('message', '').strip()

    # Validation
    if not first_name:
        return jsonify({"success": False, "message": "First name is required"}), 400
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({"success": False, "message": "Valid email is required"}), 400
    if not service:
        return jsonify({"success": False, "message": "Please select a service"}), 400

    try:
        db = get_db()
        db.execute(
            '''INSERT INTO contacts
               (first_name, last_name, email, phone, service, budget, message)
               VALUES (?,?,?,?,?,?,?)''',
            (first_name, last_name, email, phone, service, budget, message)
        )
        db.commit()

        # Return count for feedback
        count = db.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
        return jsonify({
            "success": True,
            "message": f"Thanks {first_name}! Your message has been received. We'll get back to you within 24 hours.",
            "inquiry_number": f"CFL-{1000 + count}"
        })
    except Exception as e:
        return jsonify({"success": False, "message": "Server error. Please try again."}), 500

# ─────────────────────────────────────────
# API – NEWSLETTER
# ─────────────────────────────────────────

@app.route('/api/newsletter', methods=['POST'])
def subscribe_newsletter():
    data = request.get_json()
    email = (data.get('email', '') if data else '').strip()

    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({"success": False, "message": "Please provide a valid email address"}), 400

    try:
        db = get_db()
        # Check if already subscribed
        existing = db.execute("SELECT id, active FROM newsletter WHERE email=?", (email,)).fetchone()
        if existing:
            if existing['active']:
                return jsonify({"success": False, "message": "You're already subscribed! 🎉"})
            else:
                db.execute("UPDATE newsletter SET active=1 WHERE email=?", (email,))
                db.commit()
                return jsonify({"success": True, "message": "Welcome back! You've been re-subscribed."})

        db.execute("INSERT INTO newsletter (email) VALUES (?)", (email,))
        db.commit()
        count = db.execute("SELECT COUNT(*) FROM newsletter WHERE active=1").fetchone()[0]
        return jsonify({
            "success": True,
            "message": f"🎉 You're subscribed! Join {count} others getting CAFLink insights."
        })
    except Exception as e:
        return jsonify({"success": False, "message": "Subscription failed. Please try again."}), 500

# ─────────────────────────────────────────
# API – ADMIN (READ SUBMISSIONS)
# ─────────────────────────────────────────

@app.route('/api/admin/contacts', methods=['GET'])
def admin_contacts():
    db = get_db()
    rows = db.execute("SELECT * FROM contacts ORDER BY created_at DESC").fetchall()
    return jsonify({"success": True, "data": [dict(r) for r in rows], "total": len(rows)})

@app.route('/api/admin/subscribers', methods=['GET'])
def admin_subscribers():
    db = get_db()
    rows = db.execute("SELECT * FROM newsletter WHERE active=1 ORDER BY subscribed_at DESC").fetchall()
    return jsonify({"success": True, "data": [dict(r) for r in rows], "total": len(rows)})

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

if __name__ == '__main__':
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
    init_db()
    print("🚀 CAFLink server running at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
