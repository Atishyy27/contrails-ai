import cv2
import numpy as np
import sqlite3
import json
import subprocess
import os

def extract_dct_metrics(video_path):
    # 1. Grab a frame using OpenCV
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    if not success:
        return None
    cap.release()

    # 2. Convert to Grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 3. Apply 2D DCT (The SOTA Research Hook)
    # This converts spatial data (pixels) into frequency data
    dct = cv2.dct(np.float32(gray))
    
    # 4. Calculate 'High Frequency Energy'
    # Synthetic models often leave excessive energy in the high-frequency corners
    dct_log = np.log(np.abs(dct) + 1)
    avg_energy = np.mean(dct_log)
    
    return float(avg_energy)

def get_bitrate(video_path):
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', 
        '-show_format', video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return int(data.get('format', {}).get('bit_rate', 0))

def run_analysis():
    conn = sqlite3.connect('data/deepfake_vault.db')
    cursor = conn.cursor()
    
    # Add a column for bitrate if it doesn't exist
    try:
        cursor.execute("ALTER TABLE media_vault ADD COLUMN bitrate INTEGER")
        cursor.execute("ALTER TABLE media_vault ADD COLUMN freq_score REAL")
    except:
        pass

    cursor.execute("SELECT id, file_path FROM media_vault WHERE file_path IS NOT NULL AND bitrate IS NULL")
    rows = cursor.fetchall()

    for vid_id, path in rows:
        print(f"🔬 Analyzing ID {vid_id}...")
        if not os.path.exists(path):
            continue
            
        bitrate = get_bitrate(path)
        freq_score = extract_dct_metrics(path)
        
        cursor.execute("UPDATE media_vault SET bitrate = ?, freq_score = ? WHERE id = ?", 
                       (bitrate, freq_score, vid_id))
        conn.commit()
        print(f"📊 Bitrate: {bitrate} | Freq Score: {freq_score:.4f}")

    conn.close()

if __name__ == "__main__":
    run_analysis()