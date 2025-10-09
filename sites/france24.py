# Basic France24 scraper (landing) - use selectors as starting point
from utils.fetch import get_session
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = 'https://www.france24.com'

def scrape():
    s = get_session()
    resp = s.get('https://www.france24.com/en/', timeout=10)
    soup = BeautifulSoup(resp.text, 'lxml')
    articles = []
    for a in soup.select('a.td-title-link'):
        title = a.get_text(strip=True)
        href = a.get('href')
        if not href:
            continue
        if href.startswith('/'):
            href = urljoin(BASE, href)
        articles.append({
            'title': title,
            'summary': None,
            'url': href,
            'source': 'France24',
            'published_at': None,
            'image_url': None,
            'author': None,
            'content': None
        })
    return articles
