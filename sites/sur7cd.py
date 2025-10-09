# sites/sur7cd.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime

SOURCE = "7sur7.cd"
BASE_URL = "https://www.7sur7.cd"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ActuVerseBot/1.0; +https://actuverse.com/bot)"
}

def scrape(limit=10):
    response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    blocks = soup.select("div.views-row")
    
    processed_count = 0
    for block in blocks:
        if processed_count >= limit:
            break
            
        title_tag = block.find("a")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag.get("href", "")
        if not link.startswith("http"):
            link = BASE_URL + link

        # Filtrer les liens de catégories et autres liens non-articles
        if ("/category/" in link or 
            "/tag/" in link or 
            link.endswith("/politique") or 
            link.endswith("/societe") or 
            link.endswith("/sport") or 
            link.endswith("/sante") or
            "/index.php" not in link):
            continue

        img_tag = block.find("img")
        image_url = None
        if img_tag:
            src = img_tag.get("src") or img_tag.get("data-src")
            if src and not src.startswith("http"):
                image_url = BASE_URL + src
            elif src:
                image_url = src

        print(f"    -> Processing article: {title[:60]}...")

        # ---- Étape clé : aller chercher le contenu complet ----
        try:
            article_resp = requests.get(link, headers=HEADERS, timeout=10)
            article_resp.raise_for_status()
            article_soup = BeautifulSoup(article_resp.text, "html.parser")

            # Récupérer le titre depuis la page de l'article (plus précis)
            article_title = article_soup.select_one("h1")
            if article_title:
                title = article_title.get_text(strip=True)

            # Sélection du contenu principal - essayer plusieurs sélecteurs
            content_el = (article_soup.select_one("div.field-item.even") or 
                         article_soup.select_one("div.field-name-body div.field-item") or
                         article_soup.select_one("div.article-content") or 
                         article_soup.select_one("div.content") or
                         article_soup.select_one("article .content") or
                         article_soup.select_one(".node-content"))

            content = ""
            if content_el:
                # Récupérer tous les paragraphes et textes
                paragraphs = content_el.find_all(["p", "div"], string=True) + content_el.find_all("p")
                content_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 10:  # Éviter les textes trop courts
                        content_parts.append(text)
                content = " ".join(content_parts)
            
            # Si le contenu est vide, essayer une approche plus large
            if not content:
                content_div = article_soup.select_one("div.node") or article_soup.select_one("main")
                if content_div:
                    paragraphs = content_div.find_all("p")
                    content = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

            # Date de publication
            date_el = (article_soup.select_one("span.date-display-single") or 
                      article_soup.select_one("time") or
                      article_soup.select_one(".submitted") or
                      article_soup.select_one(".date"))
            published_at = (
                date_el.get_text(strip=True) if date_el else datetime.now().strftime("%Y-%m-%d")
            )

            # Auteur (optionnel)
            author_el = (article_soup.select_one(".username") or 
                        article_soup.select_one(".author") or
                        article_soup.select_one(".submitted a"))
            author = author_el.get_text(strip=True) if author_el else "7sur7.cd"

            # Chercher une meilleure image dans l'article
            if not image_url:
                article_img = article_soup.select_one("article img, .content img, .field-name-body img")
                if article_img:
                    src = article_img.get("src") or article_img.get("data-src")
                    if src and not src.startswith("http"):
                        image_url = BASE_URL + src
                    elif src:
                        image_url = src

            if content:  # Ne garder que les articles avec du contenu
                articles.append({
                    "title": title,
                    "url": link,
                    "content": content,  # Contenu complet sans limite
                    "image_url": image_url,
                    "author": author,
                    "published_at": published_at,
                    "source": SOURCE,
                })
                processed_count += 1
                print(f"    -> ✓ Article saved: {len(content)} chars content")
            else:
                print(f"    -> ✗ No content found for: {title[:60]}")

        except Exception as e:
            print(f"    [!] Error fetching article {link}: {e}")
            continue

    return articles
