import sqlite3
import os
import hashlib

def get_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def sync():
    conn = sqlite3.connect('data/deepfake_vault.db')
    cursor = conn.cursor()
    vid_dir = "data/raw_vid"
    
    if not os.path.exists(vid_dir):
        return

    files = [f for f in os.listdir(vid_dir) if f.endswith('.mp4')]

    for f in files:
        vid_id = f.split('.')[0]
        path = os.path.normpath(os.path.join(vid_dir, f))
        
        try:
            sha = get_sha256(path)
            
            # SURGICAL FIX: Check if this hash already exists for a DIFFERENT ID
            cursor.execute("SELECT id FROM media_vault WHERE sha256_hash = ? AND id != ?", (sha, vid_id))
            duplicate = cursor.fetchone()
            
            if duplicate:
                print(f"⚠️ Collision: ID {vid_id} is a duplicate of ID {duplicate[0]}. Cleaning up.")
                # Delete the redundant file from disk
                os.remove(path)
                # Remove the redundant record from the database
                cursor.execute("DELETE FROM media_vault WHERE id = ?", (vid_id,))
            else:
                # No collision, proceed with normal sync
                cursor.execute("UPDATE media_vault SET file_path=?, sha256_hash=? WHERE id=?", (path, sha, vid_id))
                print(f"✅ Synced ID {vid_id}")
            
            conn.commit()
        except Exception as e:
            print(f"❌ Error syncing {f}: {e}")
            
    conn.close()

if __name__ == "__main__":
    sync()