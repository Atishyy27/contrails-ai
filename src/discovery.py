import praw
import os
from dotenv import load_dotenv
import sqlite3
import time

load_dotenv()

def get_reddit_instance():
    return praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )
def discover_deepfakes(subreddit_name, limit=10):
    reddit = get_reddit_instance()
    subreddit = reddit.subreddit(subreddit_name)
    conn = sqlite3.connect('data/deepfake_vault.db')
    cursor = conn.cursor()

    print(f"Scanning r/{subreddit_name}...")
    
    # Use 'hot' instead of 'new' for higher quality, but fewer requests
    for post in subreddit.hot(limit=limit):
        if post.is_video or "v.redd.it" in post.url:
            cursor.execute('''
                INSERT OR IGNORE INTO media_vault (source_url, platform, category)
                VALUES (?, ?, ?)
            ''', (post.url, 'reddit', 'unknown'))
            print(f"Logged: {post.id}")
            
        # THE SAFETY VALVE: Wait 2 seconds between posts to avoid 'Excessive Usage'
        time.sleep(2) 
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Target subreddits where deepfakes/AI videos are common
    subs = ['StableDiffusion', 'SoraAI', 'KlingAI']
    for s in subs:
        discover_deepfakes(s, limit=20)