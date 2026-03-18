"""
CAFLink - Full Stack Web Application
Backend: Flask (Python)  |  Database: SQLite
"""

import sqlite3, os, re, json
from flask import Flask, request, jsonify, render_template, g, send_from_directory

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'db', 'caflink.db')
app.config['SECRET_KEY'] = 'caflink-secret-2025'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# ── DB helpers ──────────────────────────────────────────────────────
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT NOT NULL,
        last_name TEXT, email TEXT NOT NULL, phone TEXT, service TEXT,
        budget TEXT, message TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, status TEXT DEFAULT 'new')''')
    c.execute('''CREATE TABLE IF NOT EXISTS newsletter (
        id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL,
        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, active INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS testimonials (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, role TEXT,
        company TEXT, message TEXT NOT NULL, rating INTEGER DEFAULT 5,
        avatar TEXT, approved INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
        description TEXT, icon TEXT, features TEXT, active INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT NOT NULL,
        value TEXT NOT NULL, suffix TEXT DEFAULT '+')''')

    if c.execute("SELECT COUNT(*) FROM testimonials").fetchone()[0] == 0:
        c.executemany("INSERT INTO testimonials (name,role,company,message,rating,avatar) VALUES (?,?,?,?,?,?)",[
            ("Rahul Kapoor","CTO","FinEdge Technologies","CAFLink transformed our legacy system into a sleek platform in under 3 months. Technically brilliant and beyond expectations.",5,"RK"),
            ("Priya Mehta","Founder","GrowthHive","Their digital marketing doubled our organic traffic in 60 days. The AI content strategy was game-changing for our startup.",5,"PM"),
            ("Amit Sharma","VP Engineering","RetailPulse","Infrastructure costs dropped 40% while performance improved 3x. CAFLink handled everything seamlessly.",5,"AS"),
            ("Sneha Verma","CEO","EduTech India","CAFLink built our entire e-learning platform — beautifully designed, lightning fast, and on budget. Highly recommended!",5,"SV"),
            ("Karan Joshi","Product Head","LogisticsPro","The AI automation pipeline they built saves our team 20+ hours every week. Technical depth is genuinely impressive.",5,"KJ"),
            ("Meera Iyer","Director","HealthFirst","They redesigned our patient portal and engagement metrics went through the roof. Zero downtime since launch.",5,"MI"),
        ])

    if c.execute("SELECT COUNT(*) FROM services").fetchone()[0] == 0:
        c.executemany("INSERT INTO services (title,description,icon,features) VALUES (?,?,?,?)",[
            ("Software Development","Custom software engineered for your exact workflows. Scalable architecture, clean code, continuous delivery.","💻",'["Custom ERP/CRM Systems","API Development & Integration","Mobile Applications","Microservices Architecture","Code Review & Refactoring"]'),
            ("Web Development","High-performance websites and web apps. React, Next.js, Node.js — fast, secure, beautiful.","🌐",'["React / Next.js Frontends","Node.js & Python Backends","E-Commerce Platforms","Progressive Web Apps","UI/UX Design"]'),
            ("Database Management","Architecture, optimization, migration and monitoring of your entire data layer.","🗄️",'["Database Design & Modeling","Query Optimization","Data Migration","Backup & Recovery","PostgreSQL / MongoDB / MySQL"]'),
            ("Server & Hosting","Rock-solid cloud infrastructure with 99.9% uptime SLAs on AWS, GCP and Azure.","☁️",'["Cloud Setup (AWS/GCP/Azure)","Docker & Kubernetes","CI/CD Pipelines","Auto-scaling","24/7 Monitoring"]'),
            ("Digital Marketing","SEO, SEM, social media strategy and analytics that turn traffic into revenue.","📈",'["Search Engine Optimization","Google Ads & PPC","Social Media Management","Email Campaigns","Conversion Optimization"]'),
            ("Content Creation","Brand-aligned content that resonates — blogs, graphics and UI/UX assets.","🎨",'["Brand Identity & Guidelines","Copywriting & Blogging","Infographics & Illustrations","Social Media Content","Video Production"]'),
            ("AI-Driven Platforms","Custom AI integrations, LLM-powered workflows and intelligent analytics.","🤖",'["LLM Integration (GPT/Claude)","AI Chatbot Development","Predictive Analytics","Process Automation","Computer Vision"]'),
        ])

    if c.execute("SELECT COUNT(*) FROM stats").fetchone()[0] == 0:
        c.executemany("INSERT INTO stats (label,value,suffix) VALUES (?,?,?)",[
            ("Projects Delivered","150","+"),("Client Satisfaction","98","%"),
            ("Years of Excellence","5","+"),("Expert Engineers","40","+")])

    db.commit(); db.close()
    print("✅ Database initialized.")

# ── Static image serving ─────────────────────────────────────────────
@app.route('/static/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'), filename)

# ── Pages ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ── API ───────────────────────────────────────────────────────────────
@app.route('/api/services')
def get_services():
    rows = get_db().execute("SELECT * FROM services WHERE active=1").fetchall()
    result = []
    for r in rows:
        row = dict(r)
        try: row['features'] = json.loads(row['features'] or '[]')
        except: row['features'] = []
        result.append(row)
    return jsonify({"success": True, "data": result})

@app.route('/api/testimonials')
def get_testimonials():
    rows = get_db().execute("SELECT * FROM testimonials WHERE approved=1").fetchall()
    return jsonify({"success": True, "data": [dict(r) for r in rows]})

@app.route('/api/stats')
def get_stats():
    rows = get_db().execute("SELECT * FROM stats").fetchall()
    return jsonify({"success": True, "data": [dict(r) for r in rows]})

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    data = request.get_json() or {}
    first_name = data.get('first_name','').strip()
    email      = data.get('email','').strip()
    service    = data.get('service','').strip()
    if not first_name: return jsonify({"success":False,"message":"First name is required"}),400
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email): return jsonify({"success":False,"message":"Valid email is required"}),400
    if not service: return jsonify({"success":False,"message":"Please select a service"}),400
    try:
        db = get_db()
        db.execute("INSERT INTO contacts (first_name,last_name,email,phone,service,budget,message) VALUES (?,?,?,?,?,?,?)",
            (first_name, data.get('last_name',''), email, data.get('phone',''), service, data.get('budget',''), data.get('message','')))
        db.commit()
        count = db.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
        return jsonify({"success":True,"message":f"Thanks {first_name}! We'll reply within 24 hours.","inquiry_number":f"CFL-{1000+count}"})
    except: return jsonify({"success":False,"message":"Server error. Please try again."}),500

@app.route('/api/newsletter', methods=['POST'])
def subscribe_newsletter():
    data  = request.get_json() or {}
    email = data.get('email','').strip()
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({"success":False,"message":"Please provide a valid email"}),400
    try:
        db = get_db()
        existing = db.execute("SELECT id,active FROM newsletter WHERE email=?", (email,)).fetchone()
        if existing:
            if existing['active']: return jsonify({"success":False,"message":"You're already subscribed! 🎉"})
            db.execute("UPDATE newsletter SET active=1 WHERE email=?", (email,)); db.commit()
            return jsonify({"success":True,"message":"Welcome back! You've been re-subscribed."})
        db.execute("INSERT INTO newsletter (email) VALUES (?)", (email,)); db.commit()
        count = db.execute("SELECT COUNT(*) FROM newsletter WHERE active=1").fetchone()[0]
        return jsonify({"success":True,"message":f"🎉 Subscribed! Join {count} others getting CAFLink insights."})
    except: return jsonify({"success":False,"message":"Subscription failed."}),500

@app.route('/api/admin/contacts')
def admin_contacts():
    rows = get_db().execute("SELECT * FROM contacts ORDER BY created_at DESC").fetchall()
    return jsonify({"success":True,"data":[dict(r) for r in rows],"total":len(rows)})

@app.route('/api/admin/subscribers')
def admin_subscribers():
    rows = get_db().execute("SELECT * FROM newsletter WHERE active=1 ORDER BY subscribed_at DESC").fetchall()
    return jsonify({"success":True,"data":[dict(r) for r in rows],"total":len(rows)})

# ── Start ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
    init_db()
    print("🚀 CAFLink running at http://localhost:5000")
    # REPLACE with this:
if __name__ == '__main__':
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 CAFLink running → http://localhost:{port}")
    print(f"🔐 Admin panel  → http://localhost:{port}/admin")
    app.run(debug=False, host='0.0.0.0', port=port)