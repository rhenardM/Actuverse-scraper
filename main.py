# ActuVerse scraper - orchestrator
import argparse
import importlib
import os
import pkgutil
import sys
import logging
from datetime import datetime
from utils.save import save_to_api
from utils.fetch import get_session
from utils.deduplication import filter_new_articles, log_scraping_stats
from config.settings import DRY_RUN, API_URL

SITES_PACKAGE = 'sites'

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/scraper_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Créer le dossier logs s'il n'existe pas
os.makedirs('logs', exist_ok=True)

def discover_scrapers():
    scrapers = []
    package = importlib.import_module(SITES_PACKAGE)
    for finder, name, ispkg in pkgutil.iter_modules(package.__path__):
        if name.startswith('_'):
            continue
        module = importlib.import_module(f'{SITES_PACKAGE}.{name}')
        if hasattr(module, 'scrape'):
            scrapers.append((name, module.scrape))
    return scrapers

def dedupe_by_url(articles):
    seen = set()
    out = []
    for a in articles:
        url = a.get('url') or a.get('link') or a.get('source_url')
        if not url:
            continue
        if url in seen:
            continue
        seen.add(url)
        out.append(a)
    return out

def main(dry_run=False, selected=None, show_full_content=False, check_duplicates=True, hours_filter=24):
    logger.info(f"🚀 Démarrage du scraping automatique ActuVerse")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'PRODUCTION'}")
    logger.info(f"API: {API_URL}")
    logger.info(f"Filtrage: {hours_filter}h, Vérification doublons: {check_duplicates}")
    
    scrapers = discover_scrapers()
    if selected:
        scrapers = [s for s in scrapers if s[0] in selected]
        logger.info(f"Sites sélectionnés: {selected}")
    
    all_articles = []
    total_stats = {'total': 0, 'new': 0, 'existing': 0, 'old': 0}
    
    for name, fn in scrapers:
        try:
            logger.info(f"🔍 Scraping {name}...")
            site_articles = fn()
            logger.info(f"📄 {len(site_articles)} articles bruts récupérés de {name}")
            
            if site_articles:
                # Filtrer les nouveaux articles
                new_articles, stats = filter_new_articles(
                    site_articles, 
                    check_existing=check_duplicates,
                    hours_threshold=hours_filter
                )
                
                # Mettre à jour les statistiques globales
                for key in total_stats:
                    total_stats[key] += stats[key]
                
                # Logger les stats par site
                log_scraping_stats(name, stats)
                
                all_articles.extend(new_articles)
                logger.info(f"✅ {len(new_articles)} nouveaux articles de {name} ajoutés")
            else:
                logger.warning(f"⚠️ Aucun article récupéré de {name}")
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du scraping de {name}: {e}")

    # Déduplication finale par URL (au cas où)
    all_articles = dedupe_by_url(all_articles)
    logger.info(f"📊 Total final après déduplication: {len(all_articles)} articles")
    
    # Logger les statistiques globales
    logger.info("=== STATISTIQUES GLOBALES ===")
    logger.info(f"Total articles trouvés: {total_stats['total']}")
    logger.info(f"Nouveaux articles: {total_stats['new']}")
    logger.info(f"Articles déjà existants: {total_stats['existing']}")
    logger.info(f"Articles trop anciens: {total_stats['old']}")
    
    if total_stats['total'] > 0:
        efficiency = (total_stats['new'] / total_stats['total']) * 100
        logger.info(f"Efficacité du scraping: {efficiency:.1f}%")

    if dry_run:
        # Importer le catégoriseur pour afficher les catégories en dry-run
        from utils.categorizer import categorize_article
        
        logger.info(f"=== MODE DRY RUN - APERÇU DES ARTICLES ===")
        for i, art in enumerate(all_articles[:30], 1):
            # Calculer la catégorie pour l'affichage
            category = categorize_article(
                title=art.get('title', ''),
                content=art.get('content', ''),
                source=art.get('source', '')
            )
            
            print(f"--- {i} ---")
            print(f"Title: {art.get('title')}")
            print(f"URL: {art.get('url')}")
            print(f"Author: {art.get('author', 'N/A')}")
            print(f"Published: {art.get('published_at', 'N/A')}")
            print(f"Image: {art.get('image_url', 'No image')}")
            print(f"🏷️  Catégorie: {category}")
            content = art.get('content', '')
            if content:
                print(f"Content ({len(content)} chars):")
                if show_full_content:
                    print(content)
                    print(f"[contenu complet affiché - {len(content)} caractères]")
                else:
                    # Afficher les 500 premiers caractères au lieu de 200
                    print(f"{content[:500]}...")
                    print(f"[... reste {len(content)-500} caractères ...]" if len(content) > 500 else "[contenu complet affiché]")
            else:
                print("Content: No content found")
            print(f"Source: {art.get('source', 'N/A')}")
            print()
        
        logger.info(f"=== FIN DRY RUN ===")
        return

    # Envoi vers l'API en mode production
    if all_articles:
        logger.info(f"📤 Envoi de {len(all_articles)} nouveaux articles vers l'API...")
        save_to_api(all_articles)
        logger.info(f"✅ Scraping automatique terminé avec succès")
    else:
        logger.info(f"ℹ️ Aucun nouvel article à envoyer")
        
    return len(all_articles)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ActuVerse - Scraper automatique d\'articles')
    parser.add_argument('--dry-run', action='store_true', help='Mode test : affichage seulement, pas d\'envoi API')
    parser.add_argument('--sites', nargs='*', help='Sites spécifiques à scraper (noms des modules)')
    parser.add_argument('--full-content', action='store_true', help='Afficher le contenu complet en mode dry-run')
    parser.add_argument('--no-check', action='store_true', help='Ne pas vérifier les doublons en base')
    parser.add_argument('--hours', type=int, default=24, help='Filtrer les articles des X dernières heures (défaut: 24)')
    
    args = parser.parse_args()
    
    # Configuration du scraping
    check_duplicates = not args.no_check
    
    try:
        main(
            dry_run=args.dry_run, 
            selected=args.sites, 
            show_full_content=args.full_content,
            check_duplicates=check_duplicates,
            hours_filter=args.hours
        )
    except KeyboardInterrupt:
        logger.info("🛑 Scraping interrompu par l'utilisateur")
    except Exception as e:
        logger.error(f"💥 Erreur fatale: {e}")
        sys.exit(1)
