import requests
import sqlite3

def scrape_civitai():
    # Civitai Public API for the latest images
    url = "https://civitai.com/api/v1/images?limit=50&sort=Newest&nsfw=false"
    print("🎨 Fetching high-fidelity images from Civitai...")
    
    try:
        response = requests.get(url, headers={"User-Agent": "ForensicScanner/1.0"})
        items = response.json().get('items', [])
        
        conn = sqlite3.connect('data/deepfake_vault.db')
        cursor = conn.cursor()
        
        for item in items:
            img_url = item.get('url')
            # Extracting model name to link with research papers
            model = item.get('meta', {}).get('Model', 'Latent Diffusion')
            
            cursor.execute('''
                INSERT OR IGNORE INTO media_vault (source_url, platform, category, model_name)
                VALUES (?, ?, ?, ?)
            ''', (img_url, 'civitai', 'photo', model))
            
        conn.commit()
        conn.close()
        print(f"✅ Added {len(items)} image targets.")
    except Exception as e:
        print(f"Civitai scrape failed: {e}")

if __name__ == "__main__":
    scrape_civitai()