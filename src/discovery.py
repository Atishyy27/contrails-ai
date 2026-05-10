import requests
import json
import os
import sqlite3

def run_scraper():
    # Target subreddit
    subreddit = "StableDiffusion"
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=100"
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    # Ensure folder exists
    if not os.path.exists('data'):
        os.makedirs('data')

    print(f"Connecting to r/{subreddit}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch data. Error code: {response.status_code}")
        return

    posts = response.json().get('data', {}).get('children', [])
    conn = sqlite3.connect('data/deepfake_vault.db')
    cursor = conn.cursor()

    found_count = 0
    for post in posts:
        data = post.get('data', {})
        # Check for video content
        if data.get('is_video') or "v.redd.it" in data.get('url', ''):
            source_url = data.get('url')
            # Categorize based on keywords in title
            title = data.get('title', '').lower()
            category = "animation"
            if "swap" in title:
                category = "face_swap"
            elif "sync" in title or "talk" in title:
                category = "lip_sync"
            
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO media_vault (source_url, platform, category)
                    VALUES (?, ?, ?)
                ''', (source_url, 'reddit', category))
                found_count += 1
            except Exception:
                pass

    conn.commit()
    conn.close()
    print(f"Done. Added {found_count} video targets to the database.")

if __name__ == "__main__":
    run_scraper()