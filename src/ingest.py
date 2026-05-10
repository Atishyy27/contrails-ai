import sqlite3
import subprocess
import hashlib
import os

def get_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_forensic_metadata(file_path):
    # Achievement Hook: Extracting Bitrate & Codec (Provenance)
    cmd = [
        'yt-dlp',
        '--format', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '--merge-output-format', 'mp4',
        '-o', output_template,
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    metadata = json.loads(result.stdout)
    
    # Paper Insight: Video LDM mentions bitrate impacts artifact preservation 
    bitrate = metadata.get('format', {}).get('bit_rate', 0)
    return int(bitrate)

def run_ingestion():
    conn = sqlite3.connect('data/deepfake_vault.db')
    cursor = conn.cursor()
    
    # Get targets that haven't been downloaded yet
    cursor.execute("SELECT id, source_url FROM media_vault WHERE file_path IS NULL")
    targets = cursor.fetchall()
    
    if not targets:
        print("No new targets to ingest.")
        return

    for target_id, url in targets:
        print(f"📥 Ingesting ID {target_id}: {url}")
        
        output_template = f"data/raw_vid/{target_id}.mp4"
        
        # Using yt-dlp to download the raw binary bits
        cmd = [
            'yt-dlp',
            '-f', 'mp4',
            '-o', output_template,
            url
        ]
        
        try:
            subprocess.run(cmd, check=True)
            
            # Calculate integrity hash
            file_hash = get_sha256(output_template)
            
            # Update the ledger
            cursor.execute('''
                UPDATE media_vault 
                SET sha256_hash = ?, file_path = ? 
                WHERE id = ?
            ''', (file_hash, output_template, target_id))
            conn.commit()
            print(f"✅ Verified: {file_hash}")
            
        except Exception as e:
            print(f"❌ Failed to ingest {target_id}: {e}")

    conn.close()

if __name__ == "__main__":
    run_ingestion()