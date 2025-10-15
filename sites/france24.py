# Enhanced France24 scraper - fetches full article content and metadata
from utils.fetch import get_session
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import requests
import time

BASE = 'https://www.france24.com'
SOURCE = "France24"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

def scrape(limit=10):
    print(f"    -> Starting France24 scraper...")
    
    try:
        # Essayer différentes URLs de France24
        urls_to_try = [
            'https://m.france24.com/en/',
            'https://www.france24.com/en/live-news/',
            'https://observers.france24.com/en'
        ]
        
        articles = []
        
        for base_url in urls_to_try:
            try:
                print(f"    -> Trying URL: {base_url}")
                response = requests.get(base_url, headers=HEADERS, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Chercher les liens d'articles
                article_links = find_article_links(soup, base_url)
                print(f"    -> Found {len(article_links)} potential articles from {base_url}")
                
                if article_links:
                    articles.extend(article_links)
                    break  # Si on trouve des articles, on s'arrête
                    
            except Exception as e:
                print(f"    -> Error with {base_url}: {e}")
                continue
        
        if not articles:
            print(f"    -> No articles found from any France24 URL")
            return []
        
        # Dédupliquer les articles
        unique_articles = []
        seen_urls = set()
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        print(f"    -> Processing {min(len(unique_articles), limit)} unique articles...")
        
        # Récupérer le contenu complet de chaque article
        processed_count = 0
        final_articles = []
        
        for article in unique_articles[:limit]:
            if processed_count >= limit:
                break
                
            try:
                print(f"    -> Processing article: {article['title'][:60]}...")
                
                # Récupérer la page de l'article
                article_resp = requests.get(article['url'], headers=HEADERS, timeout=15)
                article_resp.raise_for_status()
                article_soup = BeautifulSoup(article_resp.text, 'html.parser')
                
                # Extraire le contenu complet
                content = extract_article_content(article_soup)
                if not content or len(content) < 200:
                    print(f"    -> ✗ Insufficient content for: {article['title'][:60]}")
                    continue
                
                # Extraire les métadonnées
                title = extract_title(article_soup) or article['title']
                image_url = extract_image(article_soup)
                published_at = extract_date(article_soup)
                author = extract_author(article_soup)
                
                final_articles.append({
                    'title': title,
                    'url': article['url'],
                    'content': content,
                    'image_url': image_url,
                    'author': author,
                    'published_at': published_at,
                    'source': SOURCE,
                })
                
                processed_count += 1
                print(f"    -> ✓ Article saved: {len(content)} chars content")
                
                # Petite pause pour éviter d'être bloqué
                time.sleep(1)
                
            except Exception as e:
                print(f"    -> Error processing {article['url']}: {e}")
                continue
        
        print(f"    -> France24 scraper completed: {len(final_articles)} articles")
        return final_articles
        
    except Exception as e:
        print(f"    -> France24 scraper failed: {e}")
        return []

def find_article_links(soup, base_url):
    """Trouve les liens d'articles dans la page"""
    articles = []
    
    # Différents sélecteurs pour France24 (mobile et desktop)
    selectors = [
        'a[href*="/en/2"]',  # Articles avec années
        'a[href*="/en/news/"]',
        'a[href*="/en/world/"]',
        'a[href*="/en/africa/"]',
        'a[href*="/en/europe/"]',
        'a[href*="/en/middle-east/"]',
        'a[href*="/en/asia-pacific/"]',
        'a.article-link',
        'a.td-title-link',
        'h1 a, h2 a, h3 a, h4 a',
        '.article-title a',
        '.news-item a',
        '.story-link a',
        '.teaser a'
    ]
    
    for selector in selectors:
        for link in soup.select(selector):
            href = link.get('href')
            title = link.get_text(strip=True)
            
            if not href or not title or len(title) < 15:
                continue
            
            # Construire l'URL absolue
            if href.startswith('/'):
                # Si on est sur le site mobile, utiliser l'URL mobile
                if 'm.france24.com' in base_url:
                    href = 'https://www.france24.com' + href  # Convertir vers le site principal pour le contenu
                else:
                    href = urljoin(BASE, href)
            elif not href.startswith('http'):
                continue
            
            # Filtrer les liens non-articles
            if not is_valid_article_url(href):
                continue
            
            articles.append({
                'title': title,
                'url': href
            })
    
    return articles

def is_valid_article_url(url):
    """Vérifie si l'URL est un article valide"""
    if not url.startswith('https://www.france24.com'):
        return False
    
    # Exclure les pages non-articles
    exclude_patterns = [
        '/live-tv',
        '/programmes/',
        '/category/',
        '/tag/',
        '/author/',
        '/newsletter',
        '/contact',
        '/about',
        '/privacy',
        '/terms',
        '/sitemap',
        '/rss',
        '.xml',
        '.pdf',
        '/search',
        '/404'
    ]
    
    for pattern in exclude_patterns:
        if pattern in url:
            return False
    
    # Inclure les URLs qui semblent être des articles
    if any(path in url for path in ['/en/', '/news/', '/world/', '/africa/', '/europe/', '/middle-east/', '/asia-pacific/']):
        return True
        
    return False

def extract_title(soup):
    """Extraire le titre de l'article"""
    selectors = [
        'h1.article-header__title',
        'h1.t-content__title',
        'h1[itemprop="headline"]',
        '.article-title h1',
        'h1.entry-title',
        'h1.page-title',
        'h1'
    ]
    
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            title = element.get_text(strip=True)
            if title and len(title) > 5:
                return title
    
    return None

def extract_article_content(soup):
    """Extraire le contenu principal de l'article"""
    # Supprimer les éléments indésirables
    for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        element.decompose()
    
    for element in soup.find_all(class_=['advertisement', 'social-share', 'related-articles', 'comments']):
        element.decompose()
    
    # Sélecteurs pour le contenu France24
    content_selectors = [
        '.t-content__body',
        '.article-content',
        '.entry-content',
        '[itemprop="articleBody"]',
        '.post-content',
        '.article-body',
        '.content-body',
        'article .content'
    ]
    
    content = ""
    for selector in content_selectors:
        elements = soup.select(selector)
        for element in elements:
            paragraphs = element.find_all(['p', 'div'])
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 20:
                    content += text + " "
    
    # Si pas de contenu trouvé, essayer les paragraphes génériques
    if len(content) < 200:
        content = ""
        main_content = soup.select_one('main, article, .main-content')
        if main_content:
            for p in main_content.find_all('p'):
                text = p.get_text(strip=True)
                if text and len(text) > 20:
                    content += text + " "
    
    return content.strip()

def extract_image(soup):
    """Extraire l'image principale de l'article"""
    # Métadonnées OpenGraph
    meta_image = soup.select_one('meta[property="og:image"]')
    if meta_image and meta_image.get('content'):
        return meta_image['content']
    
    # Métadonnées Twitter
    twitter_image = soup.select_one('meta[name="twitter:image"]')
    if twitter_image and twitter_image.get('content'):
        return twitter_image['content']
    
    # Images dans le contenu
    img_selectors = [
        '.article-header__image img',
        '.t-content__chapo-media img',
        '.article-image img',
        '.featured-image img',
        '.post-thumbnail img',
        'article img',
        '.content img'
    ]
    
    for selector in img_selectors:
        img = soup.select_one(selector)
        if img and img.get('src'):
            src = img['src']
            if src.startswith('/'):
                src = urljoin(BASE, src)
            return src
    
    return None

def extract_date(soup):
    """Extraire la date de publication"""
    # Métadonnées
    meta_date = soup.select_one('meta[property="article:published_time"]')
    if meta_date and meta_date.get('content'):
        return meta_date['content']
    
    # Élément time
    time_element = soup.select_one('time[datetime]')
    if time_element:
        return time_element.get('datetime')
    
    # Sélecteurs spécifiques France24
    date_selectors = [
        '.article-date',
        '.published-date',
        '.date',
        '.timestamp'
    ]
    
    for selector in date_selectors:
        element = soup.select_one(selector)
        if element:
            date_text = element.get_text(strip=True)
            if date_text:
                return date_text
    
    return datetime.now().strftime("%Y-%m-%d")

def extract_author(soup):
    """Extraire l'auteur de l'article"""
    # Métadonnées
    meta_author = soup.select_one('meta[name="author"]')
    if meta_author and meta_author.get('content'):
        return meta_author['content']
    
    # Sélecteurs pour l'auteur
    author_selectors = [
        '.article-author',
        '.byline',
        '.author-name',
        '[rel="author"]',
        '.author',
        '.writer'
    ]
    
    for selector in author_selectors:
        element = soup.select_one(selector)
        if element:
            author = element.get_text(strip=True)
            if author and len(author) < 100:
                return author
    
    return "France24"
