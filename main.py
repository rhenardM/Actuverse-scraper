# ActuVerse scraper - orchestrator
import argparse
import importlib
import os
import pkgutil
import sys
from datetime import datetime
from utils.save import save_to_api
from utils.fetch import get_session
from config.settings import DRY_RUN, API_URL

SITES_PACKAGE = 'sites'

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

def main(dry_run=False, selected=None, show_full_content=False):
    scrapers = discover_scrapers()
    if selected:
        scrapers = [s for s in scrapers if s[0] in selected]
    all_articles = []
    for name, fn in scrapers:
        try:
            print(f"[+] Running scraper: {name}")
            site_articles = fn()
            print(f"    -> {len(site_articles)} items returned by {name}")
            all_articles.extend(site_articles)
        except Exception as e:
            print(f"[!] Error running {name}: {e}")

    all_articles = dedupe_by_url(all_articles)
    print(f"[+] Total unique articles: {len(all_articles)}")

    if dry_run:
        # Importer le catégoriseur pour afficher les catégories en dry-run
        from utils.categorizer import categorize_article
        
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
        return

    # send to API
    save_to_api(all_articles)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Do not post to API, only print')
    parser.add_argument('--sites', nargs='*', help='Run only specific scrapers (module names)')
    parser.add_argument('--full-content', action='store_true', help='Show full content in dry-run mode')
    args = parser.parse_args()
    main(dry_run=args.dry_run, selected=args.sites, show_full_content=args.full_content)
