# Basic BBC news scraper - landing page -> article list -> minimal fields
from utils.fetch import get_session
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

BASE = 'https://www.bbc.com'

def scrape():
    s = get_session()
    resp = s.get('https://www.bbc.com/news', timeout=10)
    soup = BeautifulSoup(resp.text, 'lxml')
    articles = []
    # Find promo links - robust fallback selectors
    for a in soup.select('a.gs-c-promo-heading, a[href*="/news/"]'):
        title = a.get_text(strip=True)
        href = a.get('href')
        if not href:
            continue
        if href.startswith('/'):
            href = urljoin(BASE, href)
        # try to get summary from adjacent paragraph
        summary = ''
        parent = a.parent
        if parent:
            p = parent.find('p')
            if p:
                summary = p.get_text(strip=True)
        articles.append({
            'title': title,
            'summary': summary,
            'url': href,
            'source': 'BBC News',
            'published_at': None,
            'image_url': None,
            'author': None,
            'content': None
        })
    # Note: for each article you can fetch the detail page and extract content, date, image.
    return articles
