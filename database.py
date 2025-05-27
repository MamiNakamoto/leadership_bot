import sqlite3

DB_NAME = "leaderboard.db"

def connect():
    return sqlite3.connect(DB_NAME)

def init_db():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adminler (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                isim TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS siralama (
                username TEXT PRIMARY KEY,
                at_etiket TEXT,
                puan INTEGER
            )
        """)
        conn.commit()

def is_admin(telegram_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM adminler WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone() is not None

def get_siralama():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, at_etiket, puan FROM siralama ORDER BY puan DESC")
        return cursor.fetchall()

def reset_siralama():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM siralama")
        conn.commit()

def puan_ekle(username, at_etiket):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT puan FROM siralama WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE siralama SET puan = puan + 1 WHERE username = ?", (username,))
        else:
            cursor.execute("INSERT INTO siralama (username, at_etiket, puan) VALUES (?, ?, 1)", (username, at_etiket))
        conn.commit()

def puan_sil(username):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT puan FROM siralama WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            puan = result[0]
            if puan <= 1:
                cursor.execute("DELETE FROM siralama WHERE username = ?", (username,))
            else:
                cursor.execute("UPDATE siralama SET puan = puan - 1 WHERE username = ?", (username,))
            conn.commit()

def add_admin(telegram_id, at_etiket, isim):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO adminler (telegram_id, username, isim) VALUES (?, ?, ?)",
                       (telegram_id, at_etiket, isim))
        conn.commit()
