import os
import sqlite3
import subprocess
import hashlib
import json
import cv2
from fractions import Fraction
from concurrent.futures import ThreadPoolExecutor

def get_chunked_hash(path):
    """Memory-efficient hashing for 4K/Long clips."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def validate_integrity(path):
    """Checks if the video is actually a valid muxed stream with frames."""
    cap = cv2.VideoCapture(path)
    is_opened = cap.isOpened()
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return is_opened and frame_count > 0

def get_media_metadata(path):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', path]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(res.stdout)
        f_data = data.get('format', {})
        v_stream = next((s for s in data.get('streams', []) if s['codec_type'] == 'video'), {})
        
        fps_str = v_stream.get('avg_frame_rate', '0/1')
        fps = float(Fraction(fps_str))
        
        return {
            'bitrate': int(f_data.get('bit_rate', 0)),
            'width': int(v_stream.get('width', 0)),
            'height': int(v_stream.get('height', 0)),
            'fps': fps,
            'duration': float(f_data.get('duration', 0)),
            'codec': v_stream.get('codec_name', 'unknown')
        }
    except: return None

def download_worker(target):
    target_id, url = target
    path = os.path.normpath(os.path.join("data", "raw_vid", f"{target_id}.mp4"))
    
    cmd = ['yt-dlp', '--max-filesize', '100M', '--socket-timeout', '20', '-o', path, url]
    
    try:
        subprocess.run(cmd, check=True, timeout=90, capture_output=True)
        
        if not os.path.exists(path): return (target_id, 'failed', None)
        
        if not validate_integrity(path):
            os.remove(path)
            return (target_id, 'corrupt', None)
            
        sha = get_chunked_hash(path)
        meta = get_media_metadata(path)
        return (target_id, 'completed', path, sha, meta)
    except:
        return (target_id, 'failed', None)

def run_ingestion():
    conn = sqlite3.connect('data/deepfake_vault.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, source_url FROM media_vault WHERE ingestion_status = 'pending'")
    targets = cursor.fetchall()

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(download_worker, targets))

    # Transactional Batch Update
    for res in results:
        if len(res) > 2: # Success
            tid, status, path, sha, meta = res
            cursor.execute('''
                UPDATE media_vault SET ingestion_status=?, file_path=?, sha256_hash=?, 
                bitrate=?, width=?, height=?, fps=?, duration=?, codec=? WHERE id=?
            ''', (status, path, sha, meta['bitrate'], meta['width'], meta['height'], 
                  meta['fps'], meta['duration'], meta['codec'], tid))
        else: # Failure
            tid, status, _ = res
            cursor.execute("UPDATE media_vault SET ingestion_status=? WHERE id=?", (status, tid))
    
    conn.commit()
    conn.close()