import cv2
import numpy as np
import sqlite3
import json
import subprocess
import os

def extract_temporal_metrics(path, frame_count=16):
    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total < frame_count:
        cap.release()
        return None

    frames = np.linspace(0, total - 1, frame_count, dtype=int)
    pmr_list = []

    for f_idx in frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        success, frame = cap.read()
        if not success: continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dct = np.abs(cv2.dct(np.float32(gray)))
        
        # Quadrant analysis (Explorer Level)
        h, w = dct.shape
        hf_quad = dct[int(h*0.8):, int(w*0.8):]
        pmr = np.max(hf_quad) / (np.mean(hf_quad) + 1e-6)
        pmr_list.append(pmr)

    cap.release()
    if not pmr_list: return None
    return float(np.mean(pmr_list)), float(np.var(pmr_list))

def extract_normalized_temporal_pmr(path, frame_count=16):
    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total < frame_count: return None

    indices = np.linspace(0, total - 1, frame_count, dtype=int)
    scores = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        success, frame = cap.read()
        if not success: continue

        # CRITICAL ISSUE #7: Resolution Standardization
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (256, 256))

        # CRITICAL ISSUE #6: Z-Score Normalization (Brightness/Contrast invariance)
        gray_f = gray.astype(np.float32)
        norm_gray = (gray_f - gray_f.mean()) / (gray_f.std() + 1e-6)

        # DCT + PMR
        dct = np.abs(cv2.dct(norm_gray))
        h, w = dct.shape
        hf_quad = dct[int(h*0.8):, int(w*0.8):]
        pmr = np.max(hf_quad) / (np.mean(hf_quad) + 1e-6)
        scores.append(pmr)

    cap.release()
    return (float(np.mean(scores)), float(np.var(scores))) if scores else None

def get_ffprobe_metadata(path):
    """Correct ffprobe JSON extraction for bitrate and dimensions."""
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', 
        '-show_format', '-show_streams', path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(res.stdout)
        f_data = data.get('format', {})
        v_stream = next((s for s in data.get('streams', []) if s['codec_type'] == 'video'), {})
        return {
            'bitrate': int(f_data.get('bit_rate', 0)),
            'width': int(v_stream.get('width', 0)),
            'height': int(v_stream.get('height', 0))
        }
    except: return None

# def run_analysis():
#     conn = sqlite3.connect('data/deepfake_vault.db')
#     cursor = conn.cursor()
    
#     # Ensure new columns exist for the 'Temporal Upgrade'
#     try:
#         cursor.execute("ALTER TABLE media_vault ADD COLUMN pmr_mean REAL")
#         cursor.execute("ALTER TABLE media_vault ADD COLUMN pmr_var REAL")
#         cursor.execute("ALTER TABLE media_vault ADD COLUMN width INTEGER")
#         cursor.execute("ALTER TABLE media_vault ADD COLUMN height INTEGER")
#     except: pass

#     cursor.execute("SELECT id, file_path FROM media_vault WHERE file_path IS NOT NULL AND pmr_mean IS NULL")
#     rows = cursor.fetchall()

#     for vid_id, path in rows:
#         print(f"🔬 Analyzing ID {vid_id}...")
#         if not os.path.exists(path): continue
            
#         # Analysis
#         metrics = extract_temporal_pmr(path)
#         meta = get_ffprobe_metadata(path)
        
#         if metrics and meta:
#             cursor.execute('''
#                 UPDATE media_vault 
#                 SET pmr_mean = ?, pmr_var = ?, bitrate = ?, width = ?, height = ? 
#                 WHERE id = ?
#             ''', (metrics[0], metrics[1], meta['bitrate'], meta['width'], meta['height'], vid_id))
#             conn.commit()

def run_analysis():
    conn = sqlite3.connect('data/deepfake_vault.db')
    cursor = conn.cursor()
    # Using pmr_mean and pmr_variance to match your data/schema.sql
    cursor.execute("SELECT id, file_path FROM media_vault WHERE file_path IS NOT NULL AND pmr_mean IS NULL")
    rows = cursor.fetchall()

    for vid_id, path in rows:
        print(f"🔬 Normalized Forensic Triage ID {vid_id}...")
        # CALL THE NORMALIZED VERSION HERE
        metrics = extract_normalized_temporal_pmr(path) 
        if metrics:
            cursor.execute("UPDATE media_vault SET pmr_mean=?, pmr_variance=? WHERE id=?", 
                           (metrics[0], metrics[1], vid_id))
            conn.commit()
            print(f"Normalized Mean PMR: {metrics[0]:.4f} | Var: {metrics[1]:.4f}")

    conn.close()

if __name__ == "__main__":
    run_analysis()