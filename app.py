from flask import Flask, abort, render_template, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3, os

ADMIN_KEY = os.getenv("ADMIN_KEY", "448848")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")


app = Flask(__name__)
app.secret_key = SECRET_KEY

# -------------------------
# Upload ayarları
# -------------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# -------------------------
# DB bağlantısı
# -------------------------
def db():
    return sqlite3.connect("database.db")

# -------------------------
# Paketleri al
# -------------------------
def get_packages():
    con = db()
    cur = con.cursor()
    cur.execute("SELECT name, photo_limit FROM packages")
    rows = cur.fetchall()
    con.close()
    return {name: limit for name, limit in rows}

# -------------------------
# DB tabloları
# -------------------------
def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT,
        package_name TEXT,
        lover_name TEXT,
        customer_name TEXT,
        message TEXT,
        special_date TEXT,
        custom_request TEXT,
        password_choice TEXT,
        site_password TEXT,
        music_choice TEXT,
        music_detail TEXT,
        contact TEXT,
        status TEXT DEFAULT 'beklemede',
        form_type TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        filename TEXT,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    )
    """)

    con.commit()
    con.close()

init_db()

# -------------------------
# FORM
# -------------------------
@app.route("/")
def form():
    return render_template("form.html", packages=get_packages())

# -------------------------
# ORTAK ADMIN RENDER
# -------------------------
def render_admin(where=None, params=()):
    con = db()
    cur = con.cursor()

    query = """
    SELECT id, order_number, package_name, lover_name,
           customer_name, message, music_choice, music_detail,
           contact, status, created_at, special_date, form_type
    FROM orders
    """
    if where:
        query += " WHERE " + where
    query += " ORDER BY created_at DESC"

    cur.execute(query, params)
    orders = cur.fetchall()

    cur.execute("SELECT order_id, filename FROM photos")
    photos = cur.fetchall()

    cur.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
    stats_raw = cur.fetchall()
    con.close()

    photo_map = {}
    for oid, fname in photos:
        photo_map.setdefault(oid, []).append(fname)

    stats = {
        "beklemede": 0,
        "hazirlaniyor": 0,
        "tamamlandi": 0,
        "iptal": 0
    }

    for s, c in stats_raw:
        stats[s] = c

    return render_template(
        "admin.html",
        orders=orders,
        photo_map=photo_map,
        stats=stats,
        percentages={}
    )

# -------------------------
# ADMIN PANEL
# -------------------------
@app.route("/admin")
def admin():
    if request.args.get("key") != ADMIN_KEY:
        abort(403)
    return render_admin()

@app.route("/admin/<form_type>")
def admin_form(form_type):
    return render_admin("form_type = ?", (form_type,))

# -------------------------
# STATUS UPDATE
# -------------------------
@app.route("/api/stats")
def api_stats():
    con = db()
    cur = con.cursor()

    cur.execute("""
    SELECT status, COUNT(*)
    FROM orders
    GROUP BY status
    """)
    rows = cur.fetchall()
    con.close()

    stats = {
        "beklemede": 0,
        "hazirlaniyor": 0,
        "tamamlandi": 0,
        "iptal": 0
    }

    for status, count in rows:
        if status in stats:
            stats[status] = count

    return stats


@app.route("/update-status", methods=["POST"])
def update_status():
    con = db()
    cur = con.cursor()
    cur.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (request.form["status"], request.form["order_id"])
    )
    con.commit()
    con.close()
    return redirect(f"/admin?key={ADMIN_KEY}")
# -------------------------
# SUBMIT
# -------------------------
@app.route("/submit", methods=["POST"])
def submit():
    data = request.form
    files = request.files.getlist("photos")

    con = db()
    cur = con.cursor()

    cur.execute("""
    INSERT INTO orders (
        form_type,
        order_number,
        package_name,
        lover_name,
        customer_name,
        message,
        special_date,
        custom_request,
        password_choice,
        site_password,
        music_choice,
        music_detail,
        contact,
        status
    )
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        "valentine",
        data.get("order_number"),
        data.get("package"),
        data.get("lover_name"),
        data.get("customer_name"),
        data.get("message"),
        data.get("special_date"),
        data.get("custom_request"),
        data.get("password_choice"),
        data.get("site_password"),
        data.get("music_choice"),
        data.get("music_detail"),
        data.get("contact"),
        "beklemede"
    ))

    order_id = cur.lastrowid

    for f in files:
        if f.filename:
            filename = f"{order_id}_{secure_filename(f.filename)}"
            f.save(os.path.join(UPLOAD_FOLDER, filename))
            cur.execute(
                "INSERT INTO photos (order_id, filename) VALUES (?,?)",
                (order_id, filename)
            )

    con.commit()
    con.close()

    return {"status": "ok"}

# -------------------------
# DELETE ORDER
# -------------------------
@app.route("/delete-order", methods=["POST"])
def delete_order():
    order_id = request.form["order_id"]
    con = db()
    cur = con.cursor()

    cur.execute("SELECT filename FROM photos WHERE order_id = ?", (order_id,))
    for (fname,) in cur.fetchall():
        path = os.path.join(UPLOAD_FOLDER, fname)
        if os.path.exists(path):
            os.remove(path)

    cur.execute("DELETE FROM photos WHERE order_id = ?", (order_id,))
    cur.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    con.commit()
    con.close()
    return redirect(f"/admin?key={ADMIN_KEY}")

