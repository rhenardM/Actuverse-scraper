#!/bin/bash

# =============================================================================
# ActuVerse - Script d'automatisation du scraping
# =============================================================================
# Ce script lance automatiquement le scraping des articles et peut être 
# configuré dans un cron job pour une exécution périodique
# =============================================================================

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/.venv"
PYTHON_SCRIPT="$SCRIPT_DIR/main.py"
LOG_DIR="$SCRIPT_DIR/logs"
LOCK_FILE="/tmp/actuverse_scraper.lock"

# Fonction de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/automation.log"
}

# Fonction de nettoyage
cleanup() {
    rm -f "$LOCK_FILE"
    log "🧹 Nettoyage terminé"
}

# Piège pour nettoyer en cas d'interruption
trap cleanup EXIT INT TERM

# =============================================================================
# VÉRIFICATIONS PRÉLIMINAIRES
# =============================================================================

# Vérifier si un autre processus est en cours
if [ -f "$LOCK_FILE" ]; then
    log "⚠️ Un autre processus de scraping est déjà en cours (lock file existe)"
    exit 1
fi

# Créer le lock file
echo $$ > "$LOCK_FILE"

# Créer le dossier de logs s'il n'existe pas
mkdir -p "$LOG_DIR"

log "🚀 Démarrage du scraping automatique ActuVerse"

# Vérifier que l'environnement virtuel existe
if [ ! -d "$VENV_PATH" ]; then
    log "❌ Environnement virtuel non trouvé: $VENV_PATH"
    exit 1
fi

# Vérifier que le script Python existe
if [ ! -f "$PYTHON_SCRIPT" ]; then
    log "❌ Script Python non trouvé: $PYTHON_SCRIPT"
    exit 1
fi

# =============================================================================
# CONFIGURATION DES PARAMÈTRES
# =============================================================================

# Paramètres par défaut
SITES="sur7cd bbc france24 mediacongo"
HOURS_FILTER=2  # Ne récupérer que les articles des 2 dernières heures
CHECK_DUPLICATES=true

# Permettre la personnalisation via variables d'environnement
SITES="${ACTUVERSE_SITES:-$SITES}"
HOURS_FILTER="${ACTUVERSE_HOURS_FILTER:-$HOURS_FILTER}"

log "📋 Configuration:"
log "   Sites: $SITES"
log "   Filtre horaire: ${HOURS_FILTER}h"
log "   Vérification doublons: $CHECK_DUPLICATES"

# =============================================================================
# EXÉCUTION DU SCRAPING
# =============================================================================

# Activer l'environnement virtuel et lancer le scraping
cd "$SCRIPT_DIR"
source "$VENV_PATH/bin/activate"

log "🔍 Lancement du scraping..."

# Construire la commande Python
PYTHON_CMD="python $PYTHON_SCRIPT --sites $SITES --hours $HOURS_FILTER"

if [ "$CHECK_DUPLICATES" = "false" ]; then
    PYTHON_CMD="$PYTHON_CMD --no-check"
fi

# Exécuter le scraping avec gestion des erreurs
if $PYTHON_CMD 2>&1 | tee -a "$LOG_DIR/scraping_$(date +%Y%m%d).log"; then
    log "✅ Scraping terminé avec succès"
    exit_code=0
else
    exit_code=$?
    log "❌ Erreur lors du scraping (code: $exit_code)"
fi

# =============================================================================
# NETTOYAGE ET MAINTENANCE
# =============================================================================

# Nettoyer les anciens logs (garder seulement les 7 derniers jours)
log "🧹 Nettoyage des anciens logs..."
find "$LOG_DIR" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true

# Statistiques rapides
log "📊 Statistiques des logs récents:"
recent_logs=$(find "$LOG_DIR" -name "scraper_*.log" -type f -mtime -1 | wc -l)
log "   Logs des dernières 24h: $recent_logs"

total_log_size=$(du -sh "$LOG_DIR" 2>/dev/null | cut -f1)
log "   Taille totale des logs: $total_log_size"

log "🏁 Script d'automatisation terminé (code: $exit_code)"
exit $exit_code
