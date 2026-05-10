import os
import json
import praw
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

# Config
SUBREDDITS = ['SoraAI', 'KlingAI', 'StableDiffusion']
LIMIT = 100 # Total targets
DATA_DIR = "deepfake_data"
MANIFEST_FILE = "manifest.json"

os.makedirs(DATA_DIR, exist_ok=True)

def download_video(url, post_id):
    """Downloads video using yt-dlp to ensure high quality."""
    outtmpl = os.path.join(DATA_DIR, f"{post_id}.%(ext)s")
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': outtmpl,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def run_pipeline():
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )

    manifest = []
    downloaded_count = 0

    for sub_name in SUBREDDITS:
        if downloaded_count >= LIMIT: break
        
        print(f"Searching r/{sub_name}...")
        subreddit = reddit.subreddit(sub_name)
        
        for post in subreddit.hot(limit=50):
            if downloaded_count >= LIMIT: break
            
            # Check if it's a video
            if post.is_video or "v.redd.it" in post.url:
                print(f"Attempting: {post.title[:50]}")
                filepath = download_video(post.url, post.id)
                
                if filepath:
                    manifest.append({
                        "id": post.id,
                        "title": post.title,
                        "url": post.url,
                        "file": os.path.basename(filepath),
                        "subreddit": sub_name
                    })
                    downloaded_count += 1
                    print(f"Success [{downloaded_count}/{LIMIT}]")

    # Save manifest
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=4)
    
    print(f"\nDone! Saved {downloaded_count} videos and manifest.json")

if __name__ == "__main__":
    run_pipeline()