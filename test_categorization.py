#!/usr/bin/env python3
"""
Test du système de catégorisation automatique des articles
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.categorizer import categorize_article, get_all_categories, validate_category

def test_categorization():
    """Test complet du système de catégorisation"""
    
    print("🧪 Tests de catégorisation automatique des articles\n")
    
    # Test cases exhaustifs
    test_articles = [
        # === POLITIQUE ===
        {
            'title': 'Le président Tshisekedi rencontre son homologue français à Paris',
            'content': 'Le président de la République démocratique du Congo, Félix Tshisekedi, a rencontré Emmanuel Macron à l\'Élysée pour discuter de coopération bilatérale.',
            'source': 'Radio Okapi',
            'expected': 'politique'
        },
        {
            'title': 'Assemblée nationale : adoption du budget 2025',
            'content': 'Les députés ont voté le budget de l\'État pour l\'exercice 2025 après de longues discussions en commission.',
            'source': 'MediaCongo',
            'expected': 'politique'
        },
        {
            'title': 'Joseph Kabila réunit l\'opposition à Nairobi',
            'content': 'L\'ancien président organise une rencontre de l\'opposition politique congolaise au Kenya.',
            'source': 'Sur7CD',
            'expected': 'politique'
        },
        
        # === ÉCONOMIE ===
        {
            'title': 'Le dollar américain baisse sur le marché de change de Kinshasa',
            'content': 'Les prix des biens de première nécessité restent élevés malgré la baisse du dollar. L\'inflation continue d\'affecter les ménages congolais.',
            'source': 'MediaCongo',
            'expected': 'économie'
        },
        {
            'title': 'Exportation de cobalt : la RDC signe un accord avec la Chine',
            'content': 'Un nouveau contrat d\'exportation de minerais stratégiques a été signé pour stimuler l\'économie nationale.',
            'source': 'Radio Okapi',
            'expected': 'économie'
        },
        {
            'title': 'La Banque centrale maintient son taux directeur à 8%',
            'content': 'Pour lutter contre l\'inflation, la BCC garde sa politique monétaire restrictive.',
            'source': 'MediaCongo',
            'expected': 'économie'
        },
        
        # === SÉCURITÉ ===
        {
            'title': 'Nord-Kivu : affrontements entre l\'armée et le M23',
            'content': 'Des combats ont éclaté près de Goma entre les FARDC et les rebelles du M23, causant le déplacement de civils.',
            'source': 'Radio Okapi',
            'expected': 'sécurité'
        },
        {
            'title': 'Ituri : la MONUSCO intervient contre les ADF',
            'content': 'Les Casques bleus ont mené une opération contre les Forces démocratiques alliées dans la région de Beni.',
            'source': 'Radio Okapi',
            'expected': 'sécurité'
        },
        {
            'title': 'Kinshasa : hausse de la criminalité dans la capitale',
            'content': 'La police nationale rapporte une augmentation des vols à main armée et des enlèvements.',
            'source': 'Sur7CD',
            'expected': 'sécurité'
        },
        
        # === SOCIÉTÉ ===
        {
            'title': 'Rentrée scolaire : manque d\'enseignants dans les écoles',
            'content': 'De nombreuses écoles primaires font face à une pénurie d\'instituteurs qualifiés pour cette nouvelle année scolaire.',
            'source': 'MediaCongo',
            'expected': 'société'
        },
        {
            'title': 'Santé : campagne de vaccination contre la rougeole',
            'content': 'Le ministère de la Santé lance une vaste campagne de vaccination des enfants de moins de 5 ans.',
            'source': 'Radio Okapi',
            'expected': 'société'
        },
        {
            'title': 'Mariage coutumier : préservation des traditions ancestrales',
            'content': 'Les communautés locales s\'efforcent de maintenir leurs rites traditionnels de mariage.',
            'source': 'Sur7CD',
            'expected': 'société'
        },
        
        # === SPORT ===
        {
            'title': 'CAN 2025 : les Léopards battent le Cameroun 2-1',
            'content': 'L\'équipe nationale de football de la RDC s\'impose face aux Lions indomptables lors des éliminatoires.',
            'source': 'Sur7CD',
            'expected': 'sport'
        },
        {
            'title': 'TP Mazembe remporte le championnat national',
            'content': 'Le club de Lubumbashi décroche son 18e titre de champion de la République démocratique du Congo.',
            'source': 'MediaCongo',
            'expected': 'sport'
        },
        {
            'title': 'Boxe : un Congolais champion d\'Afrique',
            'content': 'Le boxeur kinois remporte le titre continental des poids lourds à Johannesburg.',
            'source': 'Sur7CD',
            'expected': 'sport'
        },
        
        # === TECHNOLOGIE ===
        {
            'title': 'Startup congolaise : nouvelle application mobile de paiement',
            'content': 'Une jeune entreprise technologique développe une solution fintech pour faciliter les transactions.',
            'source': 'Tech Congo',
            'expected': 'technologie'
        },
        {
            'title': 'Internet : lancement de la 5G à Kinshasa',
            'content': 'Les opérateurs télécoms déploient le réseau de cinquième génération dans la capitale.',
            'source': 'MediaCongo',
            'expected': 'technologie'
        },
        {
            'title': 'Intelligence artificielle : formation des jeunes développeurs',
            'content': 'Un programme de formation en IA est lancé dans les universités congolaises.',
            'source': 'Radio Okapi',
            'expected': 'technologie'
        },
        
        # === INTERNATIONAL ===
        {
            'title': 'Summit between African leaders in Paris',
            'content': 'European and African heads of state meet to discuss cooperation and trade agreements.',
            'source': 'BBC News',
            'expected': 'international'
        },
        {
            'title': 'Union européenne : nouveau partenariat avec l\'Afrique',
            'content': 'Bruxelles annonce un plan d\'investissement de 10 milliards d\'euros pour le continent africain.',
            'source': 'France24',
            'expected': 'international'
        },
        {
            'title': 'ONU : résolution sur la paix en Afrique centrale',
            'content': 'Le Conseil de sécurité adopte une nouvelle résolution pour renforcer les missions de maintien de la paix.',
            'source': 'France24',
            'expected': 'international'
        },
        
        # === ENVIRONNEMENT ===
        {
            'title': 'Parc national de Virunga : protection des gorilles',
            'content': 'Les rangers intensifient leurs efforts pour protéger les gorilles de montagne contre le braconnage.',
            'source': 'Radio Okapi',
            'expected': 'environnement'
        },
        {
            'title': 'Déforestation : alarme sur le bassin du Congo',
            'content': 'Une étude révèle l\'accélération de la destruction de la forêt tropicale congolaise.',
            'source': 'France24',
            'expected': 'environnement'
        },
        {
            'title': 'Changement climatique : impact sur l\'agriculture',
            'content': 'Les agriculteurs s\'adaptent aux nouvelles conditions météorologiques pour maintenir leurs récoltes.',
            'source': 'MediaCongo',
            'expected': 'environnement'
        },
        
        # === GÉNÉRAL (cas limites) ===
        {
            'title': 'Actualités diverses du jour',
            'content': 'Résumé des événements de la journée sans thème spécifique.',
            'source': 'Actualité RDC',
            'expected': 'général'
        }
    ]
    
    # Exécution des tests
    passed = 0
    failed = 0
    
    print("📊 Résultats des tests par catégorie:\n")
    
    # Grouper par catégorie attendue
    categories_results = {}
    
    for test in test_articles:
        result = categorize_article(test['title'], test['content'], test['source'])
        expected = test['expected']
        
        if expected not in categories_results:
            categories_results[expected] = {'passed': 0, 'failed': 0, 'tests': []}
        
        is_correct = result == expected
        if is_correct:
            passed += 1
            categories_results[expected]['passed'] += 1
        else:
            failed += 1
            categories_results[expected]['failed'] += 1
        
        categories_results[expected]['tests'].append({
            'title': test['title'],
            'result': result,
            'expected': expected,
            'correct': is_correct,
            'source': test['source']
        })
    
    # Affichage des résultats par catégorie
    for category, results in categories_results.items():
        total_tests = results['passed'] + results['failed']
        success_rate = (results['passed'] / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"🏷️  {category.upper()}:")
        print(f"   ✅ Réussis: {results['passed']}/{total_tests} ({success_rate:.1f}%)")
        
        if results['failed'] > 0:
            print(f"   ❌ Échoués: {results['failed']}")
            for test in results['tests']:
                if not test['correct']:
                    print(f"      • '{test['title'][:50]}...' → {test['result']} (attendu: {test['expected']})")
        print()
    
    # Résumé global
    total_tests = passed + failed
    overall_success = (passed / total_tests) * 100 if total_tests > 0 else 0
    
    print("="*60)
    print(f"📈 RÉSUMÉ GLOBAL:")
    print(f"   Tests réussis: {passed}/{total_tests} ({overall_success:.1f}%)")
    print(f"   Tests échoués: {failed}/{total_tests}")
    print("="*60)
    
    # Test des fonctions utilitaires
    print("\n🔧 Test des fonctions utilitaires:")
    
    all_cats = get_all_categories()
    print(f"✅ get_all_categories(): {len(all_cats)} catégories disponibles")
    print(f"   {', '.join(all_cats)}")
    
    # Test de validation
    valid_tests = ['politique', 'économie', 'sport']
    invalid_tests = ['invalid', 'test', 'unknown']
    
    print(f"\n✅ validate_category():")
    for cat in valid_tests:
        result = validate_category(cat)
        print(f"   '{cat}': {result} ({'✅' if result else '❌'})")
    
    for cat in invalid_tests:
        result = validate_category(cat)
        print(f"   '{cat}': {result} ({'✅' if not result else '❌'})")
    
    return overall_success >= 80  # Seuil de réussite à 80%

def test_edge_cases():
    """Test des cas limites"""
    print("\n🧪 Test des cas limites:")
    
    edge_cases = [
        # Titre vide
        {'title': '', 'content': 'Contenu quelconque', 'source': 'Test', 'expected': 'général'},
        # Contenu vide
        {'title': 'Titre quelconque', 'content': '', 'source': 'Test', 'expected': 'général'},
        # Titre et contenu vides
        {'title': '', 'content': '', 'source': 'Test', 'expected': 'général'},
        # Titre None
        {'title': None, 'content': 'Contenu', 'source': 'Test', 'expected': 'général'},
        # Contenu None
        {'title': 'Titre', 'content': None, 'source': 'Test', 'expected': 'général'},
        # Texte très court
        {'title': 'Ok', 'content': 'Go', 'source': 'Test', 'expected': 'général'},
    ]
    
    for i, test in enumerate(edge_cases, 1):
        try:
            result = categorize_article(test['title'], test['content'], test['source'])
            status = "✅" if result == test['expected'] else "❌"
            print(f"   {status} Cas limite {i}: {result}")
        except Exception as e:
            print(f"   ❌ Cas limite {i}: Erreur - {str(e)}")

if __name__ == "__main__":
    print("🚀 Lancement des tests de catégorisation\n")
    
    # Test principal
    success = test_categorization()
    
    # Test des cas limites
    test_edge_cases()
    
    # Conclusion
    if success:
        print(f"\n🎉 Tests de catégorisation RÉUSSIS!")
        print("   Le système est prêt pour la production.")
    else:
        print(f"\n⚠️  Tests de catégorisation PARTIELLEMENT RÉUSSIS")
        print("   Des améliorations peuvent être nécessaires.")
    
    print(f"\n📝 Pour intégrer la catégorisation:")
    print(f"   1. Le système est déjà intégré dans utils/save.py")
    print(f"   2. Chaque article sera automatiquement catégorisé avant l'envoi")
    print(f"   3. Les catégories disponibles: {', '.join(get_all_categories())}")
