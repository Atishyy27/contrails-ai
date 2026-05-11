import cv2
import numpy as np
import sqlite3
import json
import subprocess
import os


def extract_dct_metrics(video_path):
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    cap.release()
    if not success: return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    dct = cv2.dct(np.float32(gray))
    dct_log = np.log(np.abs(dct) + 1)
    
    h, w = dct_log.shape
    # Isolate only the extreme HF corner where the 'grid' artifacts reside
    hf_quadrant = dct_log[int(h*0.8):, int(w*0.8):]
    
    # SURGICAL FIX: Peak-to-Mean Ratio (PMR)
    # Natural noise is distributed. AI artifacts create 'spikes' in the grid.
    # We look for the highest 'spike' relative to the average noise floor.
    peak = np.max(hf_quadrant)
    mean = np.mean(hf_quadrant) + 1e-6
    
    pmr_score = (peak / mean)
    return float(pmr_score)

def get_bitrate(video_path):
    # This remains as a fallback/verification if Ingest missed it
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', video_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return int(data.get('format', {}).get('bit_rate', 0))

def run_analysis():
    conn = sqlite3.connect('data/deepfake_vault.db')
    cursor = conn.cursor()
    
    # Idempotent column creation
    try:
        cursor.execute("ALTER TABLE media_vault ADD COLUMN bitrate INTEGER")
        cursor.execute("ALTER TABLE media_vault ADD COLUMN freq_score REAL")
    except: pass

    # Only analyze downloaded files that haven't been scored yet
    cursor.execute("SELECT id, file_path FROM media_vault WHERE file_path IS NOT NULL AND freq_score IS NULL")
    rows = cursor.fetchall()

    for vid_id, path in rows:
        print(f"🔬 Analyzing ID {vid_id}...")
        if not os.path.exists(path): continue
            
        freq_score = extract_dct_metrics(path)
        # Verify bitrate in case ingest failed it
        bitrate = get_bitrate(path)
        
        cursor.execute("UPDATE media_vault SET bitrate = ?, freq_score = ? WHERE id = ?", 
                       (bitrate, freq_score, vid_id))
        conn.commit()
        print(f"📊 Freq Score: {freq_score:.4f} | Bitrate: {bitrate}")

    conn.close()

if __name__ == "__main__":
    run_analysis()