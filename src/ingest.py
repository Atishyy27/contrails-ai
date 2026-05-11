import sqlite3
import subprocess
import hashlib
import os
import json
from concurrent.futures import ThreadPoolExecutor

def get_bitrate_metadata(file_path):
    try:
        cmd = [
            'yt-dlp',
            '--max-filesize', '100M', # Reduced for faster downloads
            '--socket-timeout', '20', 
            '--format', 'bestvideo[height<=720]+bestaudio/best', # Faster than 4K
            '-o', output_path,
            url
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(res.stdout)
        return int(data.get('format', {}).get('bit_rate', 0))
    except: return 0

def get_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # SURGICAL FIX: Chunked reading (4KB) to prevent OOM errors on large vids
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def download_worker(target):
    target_id, url = target
    output_path = f"data/raw_vid/{target_id}.mp4"
    
    cmd = [
        'yt-dlp',
        '--max-filesize', '500M',
        '--socket-timeout', '30',
        '--format', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '--merge-output-format', 'mp4',
        '-o', output_path,
        url
    ]
    
    try:
        # SURGICAL FIX: 60-second kill-switch for slow connections per your request
        subprocess.run(cmd, check=True, timeout=60)
        
        sha = get_sha256(output_path)
        bitrate = get_bitrate_metadata(output_path)
        return (target_id, output_path, sha, bitrate)
    except Exception as e:
        print(f"Skipping {target_id}: {e}")
        return None

def run_ingestion():
    conn = sqlite3.connect('data/deepfake_vault.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, source_url FROM media_vault WHERE file_path IS NULL")
    targets = cursor.fetchall()

    print(f"🚀 Starting concurrent ingestion for {len(targets)} targets...")

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(download_worker, targets))

    for res in results:
        if res:
            try:
                cursor.execute('''
                    UPDATE media_vault 
                    SET file_path=?, sha256_hash=?, bitrate=? 
                    WHERE id=?
                ''', (res[1], res[2], res[3], res[0]))
                conn.commit()
            except sqlite3.IntegrityError:
                print(f"Duplicate entry for ID {res[0]}, skipping DB update.")
                if os.parth.exists(res[1]):
                    os.remove(res[1])  # Clean up the downloaded file if DB update fails
                cursor.execute("UPDATE media_vault SET file_path=NULL WHERE id=?", (res[0],))  # Reset file_path to allow future retries
                conn.commit()
    
    conn.close()
    print("✅ Ingestion cycle complete.")

if __name__ == "__main__":
    run_ingestion()