import os, time, json, sys
import requests
from config.settings import API_URL

def save_to_api(articles):
    if not articles:
        print('[*] No articles to save.')
        return
    print(f"[*] Sending {len(articles)} articles to API: {API_URL}")
    for art in articles:
        payload = {
            'title': art.get('title'),
            'summary': art.get('summary'),
            'content': art.get('content'),
            'image_url': art.get('image_url'),
            'author': art.get('author'),
            'published_at': art.get('published_at'),
            'source_name': art.get('source', art.get('source_name')),
            'url': art.get('url'),
        }
        try:
            r = requests.post(API_URL, json=payload, timeout=10)
            if r.status_code in (200,201):
                print(f"[+] Ingested: {payload.get('title')[:60]}")
            else:
                print(f"[!] API responded {r.status_code}: {r.text}")
        except Exception as e:
            print(f"[!] Error posting article: {e}")
        time.sleep(0.2)  # small delay to avoid overwhelming API
