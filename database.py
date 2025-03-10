import sqlite3

def connect_db():
    conn = sqlite3.connect('invoice_app.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        address TEXT NOT NULL,
        gst_number TEXT UNIQUE NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku_code TEXT UNIQUE NOT NULL,
        product_name TEXT NOT NULL,
        hsn_code TEXT NOT NULL,
        price_per_unit REAL NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_no INTEGER UNIQUE NOT NULL,
        bill_date TEXT NOT NULL,
        client_id INTEGER,
        advance_paid REAL,
        signature_path TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bill_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER,
        sku_code TEXT,
        quantity INTEGER,
        amount REAL,
        FOREIGN KEY(bill_id) REFERENCES bills(id),
        FOREIGN KEY(sku_code) REFERENCES products(sku_code)
    )
    ''')
    
    conn.commit()
    return conn
