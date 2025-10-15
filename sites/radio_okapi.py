import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time
import random

def scrape(limit=10):
    """
    Scrape articles from Radio Okapi
    Radio Okapi est la radio officielle de la MONUSCO en RDC, couvrant l'actualité congolaise
    """
    base_url = "https://www.radiookapi.net"
    articles_url = f"{base_url}/actualite"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    articles = []
    
    try:
        print(f"🔍 Récupération de la page d'actualités Radio Okapi...")
        response = requests.get(articles_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Forcer l'encodage UTF-8
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Pattern pour les URLs d'articles Radio Okapi: /YYYY/MM/DD/actualite/categorie/titre
        article_pattern = re.compile(r'/20\d{2}/\d{2}/\d{2}/actualite/')
        
        # Rechercher tous les liens d'articles
        article_links = []
        seen_urls = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if article_pattern.search(href):
                full_url = urljoin(base_url, href)
                if full_url not in seen_urls:
                    # Extraire le titre depuis le texte du lien
                    title = link.get_text(strip=True)
                    if title and len(title) > 10:  # Filtrer les liens trop courts
                        article_links.append({
                            'url': full_url,
                            'title': title
                        })
                        seen_urls.add(full_url)
        
        print(f"📰 {len(article_links)} articles trouvés sur Radio Okapi")
        
        # Limiter le nombre d'articles
        if limit and len(article_links) > limit:
            article_links = article_links[:limit]
            print(f"📝 Limitation à {limit} articles")
        
        # Traitement de chaque article
        for i, article_link in enumerate(article_links, 1):
            try:
                print(f"\n🔍 Traitement article {i}/{len(article_links)}: {article_link['title'][:50]}...")
                
                # Récupérer le contenu de l'article
                time.sleep(random.uniform(1, 2))  # Délai respectueux
                article_response = requests.get(article_link['url'], headers=headers, timeout=15)
                article_response.raise_for_status()
                article_response.encoding = 'utf-8'
                
                article_soup = BeautifulSoup(article_response.content, 'html.parser')
                
                # Extraire le titre principal (plus précis que le lien)
                title = article_link['title']
                title_elem = article_soup.find('h1')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                
                # Extraire le contenu principal
                content = ""
                content_div = article_soup.find('div', class_='field-name-body')
                if content_div:
                    # Supprimer les images pour ne garder que le texte
                    for img in content_div.find_all('img'):
                        img.decompose()
                    
                    # Extraire tous les paragraphes
                    paragraphs = content_div.find_all('p')
                    content_parts = []
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 20:  # Filtrer les paragraphes trop courts
                            content_parts.append(text)
                    
                    content = '\n\n'.join(content_parts)
                
                # Extraire l'image principale
                image_url = None
                # Rechercher l'image dans le contenu
                img_elem = article_soup.find('div', class_='field-name-body')
                if img_elem:
                    img = img_elem.find('img')
                    if img and img.get('src'):
                        image_url = img['src']
                        # Vérifier si c'est une URL relative
                        if image_url.startswith('//'):
                            image_url = 'https:' + image_url
                        elif image_url.startswith('/'):
                            image_url = urljoin(base_url, image_url)
                
                # Si pas d'image dans le contenu, chercher dans les métadonnées
                if not image_url:
                    og_image = article_soup.find('meta', property='og:image')
                    if og_image and og_image.get('content'):
                        image_url = og_image['content']
                
                # Extraire la date de publication
                published_date = None
                date_elem = article_soup.find('p', string=re.compile(r'Publié le'))
                if date_elem:
                    date_text = date_elem.get_text()
                    # Extraire la date avec regex
                    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', date_text)
                    if date_match:
                        published_date = date_match.group(1)
                
                # Créer l'objet article
                if title and content and len(content) > 100:
                    article = {
                        'title': title,
                        'content': content,
                        'url': article_link['url'],
                        'image_url': image_url,
                        'source': 'Radio Okapi',
                        'published_at': published_date,
                        'author': 'Radio Okapi',
                        'category': 'Actualité RDC'
                    }
                    
                    articles.append(article)
                    print(f"   ✅ Article traité: {len(content)} caractères")
                else:
                    print(f"   ⚠️  Article ignoré (contenu insuffisant)")
                    
            except Exception as e:
                print(f"   ❌ Erreur lors du traitement de l'article: {str(e)}")
                continue
        
        print(f"\n🎉 Scraping Radio Okapi terminé: {len(articles)} articles récupérés")
        return articles
        
    except Exception as e:
        print(f"❌ Erreur lors du scraping Radio Okapi: {str(e)}")
        return []

if __name__ == "__main__":
    # Test du scraper
    articles = scrape(limit=5)
    print(f"\nTest terminé: {len(articles)} articles trouvés")