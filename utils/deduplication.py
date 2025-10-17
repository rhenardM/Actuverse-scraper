import requests
import logging
from datetime import datetime, timedelta
from config.settings import API_URL

logger = logging.getLogger(__name__)

def check_existing_articles(urls):
    """
    Vérifie quels articles existent déjà en base de données
    
    Args:
        urls (list): Liste des URLs à vérifier
        
    Returns:
        dict: {'existing': [...], 'new': [...]}
    """
    if not urls:
        return {'existing': [], 'new': []}
    
    try:
        # Envoyer les URLs à vérifier à l'API
        check_url = API_URL.replace('/articles', '/articles/check')
        response = requests.post(
            check_url, 
            json={'urls': urls}, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'existing': data.get('existing', []),
                'new': data.get('new', [])
            }
        else:
            logger.warning(f"API check failed with status {response.status_code}, treating all as new")
            return {'existing': [], 'new': urls}
            
    except Exception as e:
        logger.error(f"Error checking existing articles: {e}")
        # En cas d'erreur, traiter tous les articles comme nouveaux
        return {'existing': [], 'new': urls}

def is_recent_article(published_date, hours_threshold=24):
    """
    Vérifie si un article est récent (publié dans les X dernières heures)
    
    Args:
        published_date (str|datetime): Date de publication
        hours_threshold (int): Seuil en heures pour considérer un article comme récent
        
    Returns:
        bool: True si l'article est récent
    """
    if not published_date:
        return True  # Si pas de date, on récupère quand même
    
    try:
        if isinstance(published_date, str):
            # Parser différents formats de date
            if 'T' in published_date:
                # Format ISO avec timezone
                published_date = published_date.replace('Z', '+00:00')
                article_date = datetime.fromisoformat(published_date.replace('+00:00', ''))
            elif '/' in published_date:
                # Format DD/MM/YYYY
                article_date = datetime.strptime(published_date, '%d/%m/%Y')
            elif '-' in published_date:
                # Format YYYY-MM-DD
                article_date = datetime.strptime(published_date, '%Y-%m-%d')
            else:
                return True  # Format non reconnu, on garde l'article
        else:
            article_date = published_date
        
        # Enlever la timezone si présente pour comparaison
        if hasattr(article_date, 'tzinfo') and article_date.tzinfo:
            article_date = article_date.replace(tzinfo=None)
        
        threshold = datetime.now() - timedelta(hours=hours_threshold)
        return article_date >= threshold
        
    except Exception as e:
        logger.warning(f"Error parsing date {published_date}: {e}")
        return True  # En cas d'erreur, on récupère quand même

def extract_date_from_url(url):
    """
    Extrait la date depuis l'URL (format YYYY/MM/DD)
    
    Args:
        url (str): URL de l'article
        
    Returns:
        datetime|None: Date extraite ou None
    """
    import re
    
    # Pattern pour YYYY/MM/DD dans l'URL
    date_pattern = r'/(\d{4})/(\d{2})/(\d{2})/'
    match = re.search(date_pattern, url)
    
    if match:
        year, month, day = match.groups()
        try:
            return datetime(int(year), int(month), int(day))
        except ValueError:
            return None
    
    return None

def filter_new_articles(articles, check_existing=True, hours_threshold=24):
    """
    Filtre les articles pour ne garder que les nouveaux et récents
    
    Args:
        articles (list): Liste des articles à filtrer
        check_existing (bool): Vérifier l'existence en base
        hours_threshold (int): Seuil en heures pour considérer un article comme récent
        
    Returns:
        tuple: (nouveaux_articles, stats)
    """
    if not articles:
        return [], {'total': 0, 'new': 0, 'existing': 0, 'old': 0}
    
    stats = {'total': len(articles), 'new': 0, 'existing': 0, 'old': 0}
    
    # 1. Filtrer par date (garder seulement les articles récents)
    recent_articles = []
    for article in articles:
        # Vérifier la date de publication
        published_date = article.get('published_at') or article.get('published_date')
        
        # Si pas de date dans l'article, essayer d'extraire de l'URL
        if not published_date:
            url_date = extract_date_from_url(article.get('url', ''))
            if url_date:
                published_date = url_date
        
        if is_recent_article(published_date, hours_threshold):
            recent_articles.append(article)
        else:
            stats['old'] += 1
    
    logger.info(f"Articles récents (< {hours_threshold}h): {len(recent_articles)}/{len(articles)}")
    
    # 2. Vérifier l'existence en base si demandé
    if check_existing and recent_articles:
        urls = [article.get('url') for article in recent_articles if article.get('url')]
        check_result = check_existing_articles(urls)
        
        # Garder seulement les nouveaux articles
        new_urls = set(check_result['new'])
        new_articles = [
            article for article in recent_articles 
            if article.get('url') in new_urls
        ]
        
        stats['existing'] = len(check_result['existing'])
        stats['new'] = len(new_articles)
        
        logger.info(f"Articles nouveaux: {stats['new']}, déjà existants: {stats['existing']}")
        
        return new_articles, stats
    else:
        stats['new'] = len(recent_articles)
        return recent_articles, stats

def log_scraping_stats(source, stats):
    """
    Log les statistiques de scraping
    
    Args:
        source (str): Nom de la source
        stats (dict): Statistiques de filtrage
    """
    logger.info(f"=== Statistiques {source} ===")
    logger.info(f"Total trouvés: {stats['total']}")
    logger.info(f"Nouveaux: {stats['new']}")
    logger.info(f"Déjà existants: {stats['existing']}")
    logger.info(f"Trop anciens: {stats['old']}")
    logger.info(f"Taux de nouveauté: {(stats['new']/stats['total']*100):.1f}%" if stats['total'] > 0 else "N/A")
