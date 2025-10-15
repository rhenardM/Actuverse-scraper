# Enhanced BBC news scraper - fetches full article content and metadata
from utils.fetch import get_session
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import requests

BASE = 'https://www.bbc.com'
SOURCE = "BBC News"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ActuVerseBot/1.0; +https://actuverse.com/bot)"
}

def scrape(limit=10):
    s = get_session()
    resp = s.get('https://www.bbc.com/news', timeout=15)
    soup = BeautifulSoup(resp.text, 'lxml')
    
    articles = []
    processed_count = 0
    
    # Find all news links
    for a in soup.select('a[href*="/news/"]'):
        if processed_count >= limit:
            break
            
        title = a.get_text(strip=True)
        href = a.get('href')
        
        if not href or not title or len(title) < 15:
            continue
            
        if href.startswith('/'):
            href = urljoin(BASE, href)
            
        # Filter out non-article links (categories, live pages, etc.)
        if any(x in href for x in [
            '/topics/', '/live/', '/av/', '/videos/', 
            '/news/uk', '/news/world', '/news/business', '/news/politics',
            '/news/health', '/news/science', '/news/technology', '/news/entertainment',
            '/news/sports', '/news/england', '/news/scotland', '/news/wales',
            '/news/northern_ireland', '/news/africa', '/news/asia', '/news/australia',
            '/news/europe', '/news/latin_america', '/news/middle_east', '/news/us_canada',
            '/bbcindepth', '/bbcverify', '/in_pictures'
        ]):
            continue
            
        # Check if it's an individual article (has article ID)
        if not href.count('/') >= 5 or href.endswith('/news'):
            continue
            
        print(f"    -> Processing BBC article: {title[:60]}...")
        
        # Fetch full article content
        try:
            article_resp = requests.get(href, headers=HEADERS, timeout=15)
            article_resp.raise_for_status()
            article_soup = BeautifulSoup(article_resp.text, 'html.parser')
            
            # Get title from article page (more accurate)
            article_title = article_soup.select_one('h1')
            if article_title:
                title = article_title.get_text(strip=True)
            
            # Extract content - try multiple selectors
            content = ""
            content_selectors = [
                '[data-component="text-block"]',
                '.story-body__inner p',
                'article p',
                '[role="main"] p',
                '.post-content p',
                '.article-body p'
            ]
            
            for selector in content_selectors:
                paragraphs = article_soup.select(selector)
                if paragraphs:
                    content_parts = []
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 10:
                            content_parts.append(text)
                    content = " ".join(content_parts)
                    if content:
                        break
            
            # If still no content, try broader approach
            if not content:
                main_content = article_soup.select_one('main, article, [role="main"]')
                if main_content:
                    paragraphs = main_content.find_all('p')
                    content_parts = []
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 20:
                            content_parts.append(text)
                    content = " ".join(content_parts)
            
            # Extract image
            image_url = None
            img_selectors = [
                'meta[property="og:image"]',
                '.story-hero__image img',
                'article img',
                '.post-media img',
                'main img'
            ]
            
            for selector in img_selectors:
                img_el = article_soup.select_one(selector)
                if img_el:
                    if img_el.name == 'meta':
                        image_url = img_el.get('content')
                    else:
                        image_url = img_el.get('src') or img_el.get('data-src')
                    
                    if image_url:
                        if not image_url.startswith('http'):
                            image_url = urljoin(BASE, image_url)
                        break
            
            # Extract publication date
            published_at = None
            date_selectors = [
                'time[datetime]',
                '[data-testid="timestamp"]',
                '.date',
                'meta[name="article:published_time"]'
            ]
            
            for selector in date_selectors:
                date_el = article_soup.select_one(selector)
                if date_el:
                    if date_el.name == 'meta':
                        published_at = date_el.get('content')
                    elif date_el.name == 'time':
                        published_at = date_el.get('datetime') or date_el.get_text(strip=True)
                    else:
                        published_at = date_el.get_text(strip=True)
                    break
            
            if not published_at:
                published_at = datetime.now().strftime("%Y-%m-%d")
            
            # Extract author
            author = "BBC News"
            author_selectors = [
                '.author',
                '[data-testid="byline"]',
                '.byline',
                'meta[name="author"]'
            ]
            
            for selector in author_selectors:
                author_el = article_soup.select_one(selector)
                if author_el:
                    if author_el.name == 'meta':
                        author = author_el.get('content')
                    else:
                        author_text = author_el.get_text(strip=True)
                        if author_text and len(author_text) < 100:
                            author = author_text
                    break
            
            # Only add articles with content
            if content and len(content) > 100:
                articles.append({
                    'title': title,
                    'url': href,
                    'content': content,  # Full content without limit
                    'image_url': image_url,
                    'author': author,
                    'published_at': published_at,
                    'source': SOURCE,
                })
                processed_count += 1
                print(f"    -> ✓ BBC article saved: {len(content)} chars content")
            else:
                print(f"    -> ✗ No content found for: {title[:60]}")
                
        except Exception as e:
            print(f"    [!] Error fetching BBC article {href}: {e}")
            continue
    
    return articles
