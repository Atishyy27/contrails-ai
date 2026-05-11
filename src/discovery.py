import requests
import os
import sqlite3

def run_discovery():
    # Target Subreddits: AI-focused for deepfakes, Nature/Travel for 'Real' control group
    targets = {
        "StableDiffusion": "deepfake",
        "SoraAI": "deepfake",
        "KlingAI": "deepfake",
        "NatureIsFuckingLit": "real",
        "travel": "real"
    }
    
    headers = {'User-agent': 'ForensicScanner/1.0 by Atishay'}
    
    if not os.path.exists('data'):
        os.makedirs('data')

    conn = sqlite3.connect('data/deepfake_vault.db')
    cursor = conn.cursor()

    total_added = 0
    for subreddit, label in targets.items():
        print(f"🔍 Scanning r/{subreddit}...")
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=100"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Skipping r/{subreddit}: HTTP {response.status_code}")
                continue

            posts = response.json().get('data', {}).get('children', [])
            
            for post in posts:
                data = post.get('data', {})
                # Filter for Video content only
                if data.get('is_video') or "v.redd.it" in data.get('url', ''):
                    source_url = data.get('url')
                    title = data.get('title', '').lower()
                    
                    # Logic derived from Task 1: Categorization
                    category = label # Default to 'real' or 'deepfake'
                    if label == "deepfake":
                        if "swap" in title: category = "face_swap"
                        elif "sync" in title or "talk" in title: category = "lip_sync"
                        else: category = "animation"

                    cursor.execute('''
                        INSERT OR IGNORE INTO media_vault (source_url, platform, category)
                        VALUES (?, ?, ?)
                    ''', (source_url, 'reddit', category))
                    total_added += 1
        except Exception as e:
            print(f"Error on r/{subreddit}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Discovery complete. Total potential targets in DB: {total_added}")

if __name__ == "__main__":
    run_discovery()