
import sqlite3
from pathlib import Path

# Database location
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "invoices.db"


def get_connection():

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(DB_PATH)


def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            vendor TEXT NOT NULL COLLATE NOCASE,

            invoice_number TEXT NOT NULL COLLATE NOCASE,

            amount REAL NOT NULL,

            due_date TEXT,

            invoice_date TEXT,

            filename TEXT,

            review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(vendor, invoice_number)
        )
    """)

    # Add invoice_date to existing databases if missing
    cursor.execute("PRAGMA table_info(invoices)")
    columns = [column[1] for column in cursor.fetchall()]

    if "invoice_date" not in columns:
        cursor.execute(
            "ALTER TABLE invoices ADD COLUMN invoice_date TEXT"
       )

    # Add arithmetic verification status if missing
    cursor.execute("PRAGMA table_info(invoices)")
    columns = [column[1] for column in cursor.fetchall()]

    if "arithmetic_valid" not in columns:
        cursor.execute(
            "ALTER TABLE invoices ADD COLUMN arithmetic_valid INTEGER DEFAULT 0"
        )

        # Store successful PayPal payments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL UNIQUE,
            capture_id TEXT,
            invoice_number TEXT,
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'USD',
            status TEXT NOT NULL,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def find_duplicate(vendor, invoice_number):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, amount, review_date
        FROM invoices
        WHERE LOWER(TRIM(vendor)) = LOWER(TRIM(?))
        AND LOWER(TRIM(invoice_number)) = LOWER(TRIM(?))
    """, (vendor, invoice_number))

    result = cursor.fetchone()

    conn.close()

    return result


def save_invoice(invoice):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO invoices
            (vendor, invoice_number, invoice_date, amount, due_date, filename, arithmetic_valid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice["vendor"],
            invoice["invoice_number"],
            invoice.get("invoice_date"),
            invoice["amount"],
            invoice["due_date"],
            invoice["filename"],
            bool(invoice.get("arithmetic_valid", False))
        ))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()

def update_invoice_arithmetic_status(vendor, invoice_number, arithmetic_valid):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE invoices
        SET arithmetic_valid = ?
        WHERE LOWER(TRIM(vendor)) = LOWER(TRIM(?))
        AND LOWER(TRIM(invoice_number)) = LOWER(TRIM(?))
    """, (
        int(bool(arithmetic_valid)),
        vendor,
        invoice_number
    ))

    conn.commit()
    conn.close()


def get_all_invoices():

    conn = get_connection()

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM invoices
        ORDER BY review_date DESC
    """)

    invoices = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return invoices

def save_payment(payment):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO payments
            (order_id, capture_id, invoice_number, amount, currency, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            payment["order_id"],
            payment.get("capture_id"),
            payment.get("invoice_number"),
            payment["amount"],
            payment.get("currency", "USD"),
            payment["status"]
        ))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()

def get_all_payments():

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM payments
        ORDER BY payment_date DESC
    """)

    payments = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return payments