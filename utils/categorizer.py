"""
Système de catégorisation automatique des articles d'actualité
Adapté aux sources d'information africaines et congolaises
"""

import re

def categorize_article(title, content, source):
    """
    Catégorise automatiquement un article basé sur son titre, contenu et source
    
    Args:
        title (str): Titre de l'article
        content (str): Contenu de l'article
        source (str): Source de l'article
    
    Returns:
        str: Catégorie de l'article
    """
    if not title:
        return 'général'
    
    title_lower = title.lower()
    content_lower = content.lower() if content else ""
    combined_text = f"{title_lower} {content_lower}"
    
    # === POLITIQUE ===
    politics_keywords = [
        'politique', 'gouvernement', 'président', 'ministre', 'parlement',
        'assemblée', 'sénat', 'député', 'sénateur', 'élection', 'vote',
        'cabinet', 'premier ministre', 'opposition', 'parti politique',
        'tshisekedi', 'kabila', 'katumbi', 'bemba', 'kengo', 'lumumba',
        'kinshasa', 'palais de la nation', 'conseil des ministres',
        'constitution', 'démocratie', 'dictature', 'coup d\'état',
        'diplomatie', 'ambassadeur', 'consulat', 'chancellerie'
    ]
    
    # === ÉCONOMIE ===
    economy_keywords = [
        'économie', 'économique', 'dollar', 'franc', 'inflation', 'banque',
        'monnaie', 'devise', 'commerce', 'marché', 'prix', 'coût',
        'budget', 'finances', 'fiscal', 'investissement', 'entreprise',
        'business', 'industrie', 'production', 'exportation', 'importation',
        'pib', 'croissance', 'récession', 'bourse', 'crédit',
        'banque centrale', 'fmi', 'banque mondiale', 'dette',
        'cobalt', 'cuivre', 'or', 'diamant', 'coltan', 'minerai',
        'agriculture', 'café', 'cacao', 'huile de palme'
    ]
    
    # === SÉCURITÉ ===
    security_keywords = [
        'sécurité', 'guerre', 'conflit', 'violence', 'armée', 'militaire',
        'police', 'gendarmerie', 'soldat', 'casques bleus', 'monusco',
        'rebelle', 'milice', 'adf', 'm23', 'codeco', 'mai-mai',
        'terrorisme', 'kidnapping', 'enlèvement', 'banditisme',
        'criminalité', 'vol', 'meurtre', 'assassinat', 'attentat',
        'nord-kivu', 'sud-kivu', 'ituri', 'goma', 'bukavu', 'bunia',
        'déplacés', 'réfugiés', 'camp de déplacés', 'hcr',
        'cessez-le-feu', 'accord de paix', 'médiation'
    ]
    
    # === SOCIÉTÉ ===
    society_keywords = [
        'société', 'social', 'éducation', 'école', 'université', 'étudiant',
        'santé', 'hôpital', 'médecin', 'maladie', 'épidémie', 'vaccination',
        'ébola', 'paludisme', 'covid', 'choléra', 'rougeole',
        'famille', 'femme', 'enfant', 'jeune', 'vieux', 'âgé',
        'culture', 'tradition', 'langue', 'religion', 'église', 'mosquée',
        'catholicisme', 'protestantisme', 'islam', 'animisme',
        'mariage', 'divorce', 'naissance', 'décès', 'funérailles',
        'fête', 'célébration', 'carnaval', 'festival'
    ]
    
    # === SPORT ===
    sport_keywords = [
        'sport', 'football', 'basket', 'volleyball', 'tennis', 'boxe',
        'athlétisme', 'natation', 'cyclisme', 'rugby', 'handball',
        'championnat', 'coupe', 'match', 'équipe', 'joueur', 'entraîneur',
        'stade', 'terrain', 'ballon', 'but', 'score', 'victoire', 'défaite',
        'fifa', 'caf', 'chan', 'can', 'léopards', 'tp mazembe',
        'v.club', 'as vita club', 'dc motema pembe', 'fc saint eloi lupopo',
        'champion', 'titre', 'remporte', 'gagne', 'bat', 'battent',
        'compétition', 'tournoi', 'finale', 'demi-finale', 'qualification'
    ]
    
    # === TECHNOLOGIE ===
    tech_keywords = [
        'technologie', 'numérique', 'digital', 'internet', 'web',
        'smartphone', 'téléphone', 'mobile', 'ordinateur', 'laptop',
        'application', 'app', 'logiciel', 'software', 'programme',
        'intelligence artificielle', 'ia', 'robot', 'automatisation',
        'blockchain', 'cryptomonnaie', 'bitcoin', 'fintech',
        'startup', 'innovation', 'recherche', 'développement',
        'télécommunication', 'réseau', '4g', '5g', 'fibre optique'
    ]
    
    # === INTERNATIONAL ===
    # Basé sur la source et les références géographiques
    international_sources = ['BBC News', 'France24']
    international_keywords = [
        'international', 'mondial', 'global', 'planète', 'monde',
        'états-unis', 'amérique', 'europe', 'asie', 'chine', 'russie',
        'france', 'belgique', 'allemagne', 'royaume-uni', 'onu',
        'union africaine', 'cedeao', 'sadc', 'cemac', 'comesa',
        'union européenne', 'otan', 'g7', 'g20', 'sommet',
        'coopération', 'aide', 'partenariat', 'accord bilatéral'
    ]
    
    # === ENVIRONNEMENT ===
    environment_keywords = [
        'environnement', 'climat', 'réchauffement', 'pollution',
        'déforestation', 'forêt', 'parc national', 'biodiversité',
        'conservation', 'écologie', 'écologique', 'vert', 'durable',
        'carbone', 'émission', 'gaz', 'effet de serre',
        'congo basin', 'virunga', 'garamba', 'upemba', 'kundelungu',
        'fleuve congo', 'lac tanganyika', 'lac kivu', 'lac albert',
        'changement climatique', 'impact', 'météorologique',
        'gorilles', 'rangers', 'braconnage', 'protection', 'faune'
    ]
    
    # === LOGIQUE DE CATÉGORISATION ===
    
    # Vérifier chaque catégorie en comptant les mots-clés trouvés
    categories_scores = {
        'politique': sum(1 for keyword in politics_keywords if keyword in combined_text),
        'économie': sum(1 for keyword in economy_keywords if keyword in combined_text),
        'sécurité': sum(1 for keyword in security_keywords if keyword in combined_text),
        'société': sum(1 for keyword in society_keywords if keyword in combined_text),
        'sport': sum(1 for keyword in sport_keywords if keyword in combined_text),
        'technologie': sum(1 for keyword in tech_keywords if keyword in combined_text),
        'environnement': sum(1 for keyword in environment_keywords if keyword in combined_text),
        'international': sum(1 for keyword in international_keywords if keyword in combined_text)
    }
    
    # Bonus pour les sources internationales
    if source in international_sources:
        categories_scores['international'] += 2
    
    # Bonus pour Radio Okapi (souvent politique/sécurité)
    if source == 'Radio Okapi':
        categories_scores['politique'] += 1
        categories_scores['sécurité'] += 1
    
    # Bonus pour MediaCongo (souvent économie/société)
    if source == 'MediaCongo':
        categories_scores['économie'] += 1
        categories_scores['société'] += 1
    
    # Trouver la catégorie avec le score le plus élevé
    best_category = max(categories_scores, key=categories_scores.get)
    best_score = categories_scores[best_category]
    
    # Si aucun mot-clé n'est trouvé, retourner 'général'
    if best_score == 0:
        return 'général'
    
    return best_category

def get_all_categories():
    """
    Retourne la liste de toutes les catégories disponibles
    """
    return [
        'politique',
        'économie', 
        'sécurité',
        'société',
        'sport',
        'technologie',
        'international',
        'environnement',
        'général'
    ]

def validate_category(category):
    """
    Valide qu'une catégorie est dans la liste des catégories acceptées
    """
    return category in get_all_categories()

# Tests de la fonction
if __name__ == "__main__":
    # Test cases
    test_articles = [
        {
            'title': 'Le président Tshisekedi rencontre son homologue français',
            'content': 'Le président de la République démocratique du Congo...',
            'source': 'Radio Okapi',
            'expected': 'politique'
        },
        {
            'title': 'Le dollar baisse sur le marché de Kinshasa',
            'content': 'Les prix des biens de première nécessité...',
            'source': 'MediaCongo',
            'expected': 'économie'
        },
        {
            'title': 'Les Léopards battent le Cameroun 2-1',
            'content': 'L\'équipe nationale de football...',
            'source': 'Sur7CD',
            'expected': 'sport'
        },
        {
            'title': 'Nouveau smartphone lancé au Congo',
            'content': 'Une startup congolaise développe...',
            'source': 'Tech Congo',
            'expected': 'technologie'
        }
    ]
    
    print("🧪 Tests de catégorisation automatique:")
    for i, test in enumerate(test_articles, 1):
        result = categorize_article(test['title'], test['content'], test['source'])
        status = "✅" if result == test['expected'] else "❌"
        print(f"{status} Test {i}: '{test['title'][:40]}...' → {result} (attendu: {test['expected']})")
