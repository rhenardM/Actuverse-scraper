# 🤖 Guide d'Automatisation ActuVerse

Ce guide explique comment configurer l'automatisation complète du scraping pour récupérer automatiquement les nouveaux articles.

## 🎯 Fonctionnalités automatiques

✅ **Détection des nouveaux articles** : Seuls les articles non présents en base sont récupérés  
✅ **Filtrage temporel** : Récupération des articles récents uniquement (configurable)  
✅ **Catégorisation automatique** : Chaque article est catégorisé avant envoi  
✅ **Logging complet** : Traçage de toutes les opérations  
✅ **Protection contre les doublons** : Vérification en base avant insertion  

## 🚀 Utilisation

### Mode manuel avec nouvelles fonctionnalités

```bash
# Récupérer seulement les nouveaux articles des dernières 24h
python main.py --sites france24 sur7cd

# Récupérer les articles des 2 dernières heures seulement
python main.py --sites bbc --hours 2

# Mode test avec affichage des nouveaux articles détectés
python main.py --sites mediacongo --dry-run

# Désactiver la vérification des doublons (récupérer tous les articles)
python main.py --sites sur7cd --no-check

# Récupérer les articles de la dernière semaine
python main.py --sites france24 --hours 168
```

### Script d'automatisation

```bash
# Lancer le script d'automatisation (mode production)
./run_scraper.sh

# Le script utilise automatiquement :
# - Filtre 2 heures par défaut
# - Vérification des doublons activée
# - Tous les sites configurés
# - Logging complet
```

## ⚙️ Configuration du Cron Job

### 1. Éditer la crontab
```bash
crontab -e
```

### 2. Exemples de configuration

```bash
# Toutes les heures
0 * * * * /Users/user/Documents/Workspace/ActuVerse/Scraper/Test/actuverse_scraper/run_scraper.sh

# Toutes les 30 minutes
*/30 * * * * /Users/user/Documents/Workspace/ActuVerse/Scraper/Test/actuverse_scraper/run_scraper.sh

# Toutes les 15 minutes (haute fréquence)
*/15 * * * * /Users/user/Documents/Workspace/ActuVerse/Scraper/Test/actuverse_scraper/run_scraper.sh

# Tous les jours à 8h et 20h
0 8,20 * * * /Users/user/Documents/Workspace/ActuVerse/Scraper/Test/actuverse_scraper/run_scraper.sh

# Du lundi au vendredi à 9h, 12h, 15h, 18h
0 9,12,15,18 * * 1-5 /Users/user/Documents/Workspace/ActuVerse/Scraper/Test/actuverse_scraper/run_scraper.sh
```

### 3. Configuration recommandée pour ActuVerse
```bash
# Scraping toutes les heures pendant les heures de bureau
0 8-22 * * * /path/to/actuverse_scraper/run_scraper.sh

# Scraping réduit la nuit et le weekend
0 0,6,12,18 * * 0,6 /path/to/actuverse_scraper/run_scraper.sh
```

## 🛠️ Personnalisation

### Variables d'environnement pour run_scraper.sh

```bash
# Modifier les sites à scraper
export ACTUVERSE_SITES="france24 bbc"

# Modifier le filtre horaire (en heures)
export ACTUVERSE_HOURS_FILTER=1

# Puis lancer
./run_scraper.sh
```

### Paramètres avancés

```bash
# Scraping avec paramètres personnalisés
python main.py \
  --sites france24 sur7cd \
  --hours 6 \
  --no-check

# Affichage complet en mode test
python main.py \
  --sites bbc \
  --dry-run \
  --full-content \
  --hours 12
```

## 📊 Monitoring et Logs

### Localisation des logs
```
logs/
├── automation.log          # Logs du script d'automatisation
├── scraper_YYYYMMDD.log   # Logs détaillés par jour
└── scraping_YYYYMMDD.log  # Sortie complète du scraping
```

### Commandes de monitoring
```bash
# Voir les derniers logs en temps réel
tail -f logs/automation.log

# Statistiques du jour
grep "STATISTIQUES GLOBALES" logs/scraper_$(date +%Y%m%d).log

# Compter les nouveaux articles du jour
grep "nouveaux articles" logs/scraper_$(date +%Y%m%d).log | wc -l

# Voir les erreurs récentes
grep "ERROR\|❌" logs/scraper_$(date +%Y%m%d).log
```

## 🔧 Dépannage

### Problèmes courants

1. **Aucun nouvel article récupéré**
   ```bash
   # Vérifier avec un filtre plus large
   python main.py --sites france24 --hours 48 --dry-run
   ```

2. **Erreur de connexion API**
   ```bash
   # Tester la connexion à l'API
   curl -X POST "http://127.0.0.1:8000/api/articles/check" \
     -H "Content-Type: application/json" \
     -d '{"urls":["test"]}'
   ```

3. **Script d'automatisation bloqué**
   ```bash
   # Supprimer le lock file
   rm -f /tmp/actuverse_scraper.lock
   ```

### Désactiver temporairement l'automatisation
```bash
# Commenter la ligne dans crontab
crontab -e
# Ajouter # devant la ligne de scraping

# Ou désactiver complètement
crontab -r
```

## 📈 Optimisation des performances

### Réglages recommandés par contexte

**Actualités en temps réel** (15-30 min)
```bash
*/15 * * * * /path/to/run_scraper.sh
export ACTUVERSE_HOURS_FILTER=1
```

**Actualités quotidiennes** (2-6 heures)
```bash
0 */4 * * * /path/to/run_scraper.sh
export ACTUVERSE_HOURS_FILTER=8
```

**Archivage hebdomadaire** (1-7 jours)
```bash
0 0 * * 0 /path/to/run_scraper.sh
export ACTUVERSE_HOURS_FILTER=168
```

## 🛡️ Sécurité et maintenance

### Rotation des logs
```bash
# Nettoyage automatique (dans run_scraper.sh)
find logs/ -name "*.log" -type f -mtime +7 -delete
```

### Sauvegarde des configurations
```bash
# Sauvegarder la crontab actuelle
crontab -l > backup_crontab.txt

# Sauvegarder les logs importants
cp logs/automation.log backup/automation_$(date +%Y%m%d).log
```

### Surveillance de l'espace disque
```bash
# Vérifier l'espace utilisé par les logs
du -sh logs/

# Nettoyer manuellement si nécessaire
find logs/ -name "*.log" -type f -mtime +3 -delete
```

## 🎯 Résumé

Une fois configuré, le système automatique :

1. ✅ **Détecte automatiquement** les nouveaux articles sur vos sites ciblés
2. ✅ **Évite les doublons** en vérifiant l'existence en base
3. ✅ **Filtre par date** pour ne récupérer que les articles récents
4. ✅ **Catégorise automatiquement** chaque article
5. ✅ **Envoie vers votre API** Symfony en temps réel
6. ✅ **Log toutes les opérations** pour monitoring et debugging

**🎉 Votre plateforme ActuVerse sera alimentée automatiquement en contenu frais !**
