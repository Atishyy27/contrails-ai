# every video->enc to sha256_hash
import sqlite3
import os

def init_db():
    # ensureing data dir exists
    os.makedirs('data', exist_ok=True)

    conn = sqlite3.connect('data/deepfake_vault.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS media_vault (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sha256_hash TEXT UNIQUE,
        source_url TEXT,
        platform TEXT,
        category TEXT,  -- lip_sync, face_swap, animation
        model_name TEXT, -- Kling, Luma
        file_path TEXT,
        metadata_path TEXT,
        captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("vault database initialized successfully.")

if(__name__ == "__main__"):
    init_db()