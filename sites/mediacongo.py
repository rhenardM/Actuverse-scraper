# sites/mediacongo.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime

SOURCE = "MediaCongo"
RSS_URL = "https://www.mediacongo.net/rss/rss.xml"

def scrape(limit=10):  # ✅ nom changé pour être compatible avec main.py
    response = requests.get(RSS_URL, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "xml")

    items = soup.find_all("item")[:limit]
    articles = []

    for item in items:
        title = item.title.get_text(strip=True)
        link = item.link.get_text(strip=True)
        summary = item.description.get_text(strip=True)
        pub_date = item.pubDate.get_text(strip=True) if item.pubDate else datetime.now().strftime("%Y-%m-%d")

        media = item.find("enclosure") or item.find("media:content")
        image_url = media["url"] if media and media.get("url") else None

        articles.append({
            "title": title,
            "summary": summary[:300],
            "url": link,
            "image_url": image_url,
            "source": SOURCE,
            "published_at": pub_date,
        })
    return articles
