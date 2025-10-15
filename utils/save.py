import os, time, json, sys
import requests
from config.settings import API_URL

def save_to_api(articles):
    if not articles:
        print('[*] No articles to save.')
        return
    print(f"[*] Sending {len(articles)} articles to API: {API_URL}")
    for art in articles:
        # Adapter le payload aux champs attendus par Symfony
        payload = {
            'title': art.get('title'),
            'url': art.get('url'),
            'content': art.get('content'),
            'image': art.get('image_url'),  # Symfony attend 'image', pas 'image_url'
            'source': art.get('source'),
            'publishedAt': art.get('published_at', 'now')  # Symfony attend 'publishedAt'
        }
        
        # Nettoyer les valeurs None
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            print(f"[->] Sending: {payload.get('title', '')[:60]}...")
            r = requests.post(API_URL, json=payload, timeout=10)
            if r.status_code in (200, 201):
                print(f"[+] ✅ Saved: {payload.get('title', '')[:60]}")
            else:
                print(f"[!] ❌ API responded {r.status_code}: {r.text}")
                print(f"[!] Payload was: {json.dumps(payload, indent=2)}")
        except Exception as e:
            print(f"[!] ❌ Error posting article: {e}")
        time.sleep(0.2)  # small delay to avoid overwhelming API
