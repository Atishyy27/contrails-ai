import sqlite3
import os

def init_db():
    db_path = 'data/deepfake_vault.db'
    schema_path = 'data/schema.sql'
    
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    
    conn.close()
    print("Database initialized with Forensic Schema.")

if __name__ == "__main__":
    init_db()