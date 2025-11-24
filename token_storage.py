import sqlite3

# Bazaga ulanish
conn = sqlite3.connect("tokens.db")
cursor = conn.cursor()

# Jadvalni yaratish (faqat bir marta)
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_tokens (
    user_id INTEGER PRIMARY KEY,
    token TEXT
)
""")
conn.commit()

# Token saqlash
def set_token(user_id, token):
    cursor.execute("""
    INSERT OR REPLACE INTO user_tokens(user_id, token)
    VALUES (?, ?)
    """, (user_id, token))
    conn.commit()

# Token olish
def get_token(user_id):
    cursor.execute("SELECT token FROM user_tokens WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else None

# Token o'chirish (agar xohlansa)
def delete_token(user_id):
    cursor.execute("DELETE FROM user_tokens WHERE user_id=?", (user_id,))
    conn.commit()
