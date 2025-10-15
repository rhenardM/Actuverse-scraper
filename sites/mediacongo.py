# Enhanced MediaCongo scraper - fetches full article content and metadata
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import time

SOURCE = "MediaCongo"
BASE_URL = "https://www.mediacongo.net"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

def scrape(limit=10):
    print(f"    -> Starting MediaCongo scraper...")
    
    try:
        # Essayer différentes URLs de MediaCongo
        urls_to_try = [
            'https://www.mediacongo.net/',
            'https://www.mediacongo.net/actualite/',
            'https://www.mediacongo.net/politique/',
            'https://www.mediacongo.net/economie/'
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
            print(f"    -> No articles found from any MediaCongo URL")
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
        
        print(f"    -> MediaCongo scraper completed: {len(final_articles)} articles")
        return final_articles
        
    except Exception as e:
        print(f"    -> MediaCongo scraper failed: {e}")
        return []

def find_article_links(soup, base_url):
    """Trouve les liens d'articles dans la page"""
    articles = []
    
    # Tous les liens de la page
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link.get('href')
        title = link.get_text(strip=True)
        
        if not href or not title or len(title) < 15:
            continue
        
        # Construire l'URL absolue
        if href.startswith('/'):
            href = urljoin(BASE_URL, href)
        elif not href.startswith('http'):
            # Liens relatifs spécifiques à MediaCongo
            if href.endswith('.html') and 'article-actualite' in href:
                href = urljoin(BASE_URL, href)
            else:
                continue
        
        # Filtrer pour garder seulement les articles MediaCongo
        if not is_valid_mediacongo_article(href):
            continue
        
        articles.append({
            'title': title,
            'url': href
        })
    
    return articles

def is_valid_mediacongo_article(url):
    """Vérifie si l'URL est un article valide MediaCongo"""
    # Pattern spécifique des articles MediaCongo
    if 'article-actualite-' in url and '.html' in url:
        return True
    
    # Autres patterns possibles
    if 'dossier-mediacongo-' in url and '.html' in url:
        return True
    
    # Exclure les pages non-articles
    exclude_patterns = [
        'contact', 'about', 'mentions', 'privacy', 'terms',
        'javascript:', 'mailto:', '#', 'categories.html',
        'emplois.html', 'vous.html', 'images.html',
        'publireportages-reportage'
    ]
    
    for pattern in exclude_patterns:
        if pattern in url.lower():
            return False
    
    return False

def extract_title(soup):
    """Extraire le titre de l'article"""
    selectors = [
        'h1.article-title',
        'h1.entry-title',
        'h1.post-title',
        '.article-header h1',
        '.content-header h1',
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
    
    for element in soup.find_all(class_=['advertisement', 'social-share', 'related-articles', 'comments', 'sidebar']):
        element.decompose()
    
    # Sélecteurs pour le contenu MediaCongo (spécifiques à leur structure)
    content_selectors = [
        '[class*="text"]',  # MediaCongo utilise des classes avec "text"
        '.article-content',
        '.entry-content',
        '.post-content',
        '.content-body',
        '[itemprop="articleBody"]',
        '.article-body'
    ]
    
    content = ""
    for selector in content_selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(strip=True)
            # Prendre le texte le plus long qui semble être le contenu principal
            if text and len(text) > 200:
                content = text
                break
        if content:
            break
    
    # Si pas de contenu trouvé, essayer les paragraphes dans l'ordre
    if len(content) < 200:
        content = ""
        paragraphs = soup.find_all('p')
        content_parts = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 30:  # Paragraphes substantiels
                content_parts.append(text)
        
        # Prendre les paragraphes qui semblent faire partie du contenu principal
        if content_parts:
            # Exclure les premiers paragraphes qui sont souvent des liens/navigation
            main_content = content_parts[2:] if len(content_parts) > 5 else content_parts
            content = " ".join(main_content)
    
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
        '.article-image img',
        '.featured-image img',
        '.post-thumbnail img',
        'article img',
        '.content img',
        '.entry-content img'
    ]
    
    for selector in img_selectors:
        img = soup.select_one(selector)
        if img and img.get('src'):
            src = img['src']
            if src.startswith('/'):
                src = urljoin(BASE_URL, src)
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
    
    # Sélecteurs spécifiques MediaCongo
    date_selectors = [
        '.article-date',
        '.published-date',
        '.post-date',
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
        '.post-author',
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
    
    return "MediaCongo"
