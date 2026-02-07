import sqlite3

def db():
    return sqlite3.connect("database.db")

def init_db():
    con = db()
    cur = con.cursor()

    # Packages
    cur.execute("""
    CREATE TABLE IF NOT EXISTS packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        photo_limit INTEGER
    )
    """)

    cur.execute("""
    INSERT OR IGNORE INTO packages (name, photo_limit)
    VALUES
        ('basic', 10),
        ('plus', 25),
        ('premium', 50)
    """)

    # Orders
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_type TEXT,
    order_number TEXT,
    package_name TEXT,
    lover_name TEXT,
    customer_name TEXT,
    message TEXT,
    special_date TEXT,
    custom_request TEXT,
    password_choice TEXT,
    site_password TEXT,
    contact TEXT,
    status TEXT DEFAULT 'beklemede',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)

    )
    """)

    # Photos
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

if __name__ == "__main__":
    init_db()
    print("Database hazır 🚀")
