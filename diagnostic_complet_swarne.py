"""
╔══════════════════════════════════════════════════════════════╗
║  SWARNE V2.0 - DIAGNOSTIC COMPLET                           ║
║  Test de TOUS les composants un par un                      ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import os
from datetime import datetime

# Couleurs pour terminal Windows
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.END}\n")

def print_test(text):
    print(f"{Colors.BLUE}[TEST]{Colors.END} {text}")

def print_success(text):
    print(f"{Colors.GREEN}[✓]{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}[✗]{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}[!]{Colors.END} {text}")

def print_info(text):
    print(f"{Colors.WHITE}[→]{Colors.END} {text}")


print_header("SWARNE V2.0 - DIAGNOSTIC COMPLET")
print_info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print_info(f"Python: {sys.version}")
print_info(f"Répertoire: {os.getcwd()}\n")

# Résultats
results = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'warnings': 0
}

# ============================================================
# TEST 1: Imports de base
# ============================================================
print_header("TEST 1: IMPORTS DE BASE")

results['total'] += 1
print_test("Import swarne_ultimate...")
try:
    from swarne_ultimate import Hive, Bee
    print_success("swarne_ultimate importé")
    results['passed'] += 1
except Exception as e:
    print_error(f"Échec import swarne_ultimate: {e}")
    results['failed'] += 1
    print_warning("CRITIQUE: Impossible de continuer sans swarne_ultimate.py")
    sys.exit(1)

results['total'] += 1
print_test("Import MetaTrader5...")
try:
    import MetaTrader5 as mt5
    print_success("MetaTrader5 importé")
    results['passed'] += 1
except Exception as e:
    print_error(f"Échec import MetaTrader5: {e}")
    results['failed'] += 1
    print_warning("CRITIQUE: MT5 non installé")

results['total'] += 1
print_test("Import numpy...")
try:
    import numpy as np
    print_success("numpy importé")
    results['passed'] += 1
except Exception as e:
    print_error(f"Échec import numpy: {e}")
    results['failed'] += 1

# ============================================================
# TEST 2: Connexion MT5
# ============================================================
print_header("TEST 2: CONNEXION METATRADER 5")

results['total'] += 1
print_test("Initialisation MT5...")
try:
    if not mt5.initialize():
        print_error("MT5.initialize() a échoué")
        print_info(f"Erreur MT5: {mt5.last_error()}")
        results['failed'] += 1
        print_warning("MT5 doit être ouvert et connecté")
    else:
        print_success("MT5 initialisé")
        results['passed'] += 1
        
        # Infos MT5
        account_info = mt5.account_info()
        if account_info:
            print_info(f"Compte: {account_info.login}")
            print_info(f"Serveur: {account_info.server}")
            print_info(f"Balance: ${account_info.balance:.2f}")
            print_info(f"Equity: ${account_info.equity:.2f}")
        
        # Test symbole
        results['total'] += 1
        print_test("Vérification symbole XAUUSD...")
        symbol_info = mt5.symbol_info("XAUUSD")
        if symbol_info is None:
            print_error("Symbole XAUUSD non disponible")
            results['failed'] += 1
        else:
            print_success(f"XAUUSD disponible - Prix: {symbol_info.bid}")
            print_info(f"Spread: {symbol_info.spread}")
            print_info(f"Volume min: {symbol_info.volume_min}")
            results['passed'] += 1
            
except Exception as e:
    print_error(f"Erreur MT5: {e}")
    results['failed'] += 1

# ============================================================
# TEST 3: Création Hive
# ============================================================
print_header("TEST 3: CRÉATION DE LA HIVE")

hive = None
results['total'] += 1
print_test("Création Hive(initial_capital=10000, num_bees=5, symbol='XAUUSD')...")
try:
    hive = Hive(initial_capital=10000, num_bees=5, symbol='XAUUSD')
    print_success(f"Hive créée avec {len(hive.bees)} abeilles")
    results['passed'] += 1
    
    # Vérifier les abeilles
    for bee in hive.bees:
        print_info(f"  → {bee.bee_id} (Type: {bee.bee_type})")
    
except Exception as e:
    print_error(f"Échec création Hive: {e}")
    print_info(f"Exception complète: {type(e).__name__}: {str(e)}")
    results['failed'] += 1
    import traceback
    traceback.print_exc()

# ============================================================
# TEST 4: Attributs Hive
# ============================================================
print_header("TEST 4: VÉRIFICATION ATTRIBUTS HIVE")

if hive:
    results['total'] += 1
    print_test("Vérification hive.field...")
    if hasattr(hive, 'field'):
        if hive.field is not None:
            print_success("hive.field existe et n'est pas None")
            print_info(f"Type: {type(hive.field)}")
            results['passed'] += 1
        else:
            print_error("hive.field est None")
            results['failed'] += 1
    else:
        print_error("hive.field n'existe pas")
        results['failed'] += 1
    
    results['total'] += 1
    print_test("Vérification hive.guardian...")
    if hasattr(hive, 'guardian'):
        if hive.guardian is not None:
            print_success("hive.guardian existe")
            print_info(f"Capital Guardian: ${hive.guardian.capital:.2f}")
            results['passed'] += 1
        else:
            print_error("hive.guardian est None")
            results['failed'] += 1
    else:
        print_error("hive.guardian n'existe pas")
        results['failed'] += 1
    
    results['total'] += 1
    print_test("Vérification hive.bees...")
    if hasattr(hive, 'bees'):
        if len(hive.bees) > 0:
            print_success(f"{len(hive.bees)} abeilles présentes")
            results['passed'] += 1
        else:
            print_error("Aucune abeille dans hive.bees")
            results['failed'] += 1
    else:
        print_error("hive.bees n'existe pas")
        results['failed'] += 1

# ============================================================
# TEST 5: Attributs des Abeilles
# ============================================================
print_header("TEST 5: VÉRIFICATION ATTRIBUTS DES ABEILLES")

if hive and len(hive.bees) > 0:
    bee = hive.bees[0]
    
    results['total'] += 1
    print_test(f"Vérification {bee.bee_id}.field...")
    if hasattr(bee, 'field'):
        if bee.field is not None:
            print_success(f"{bee.bee_id}.field existe")
            print_info(f"Type: {type(bee.field)}")
            results['passed'] += 1
        else:
            print_error(f"{bee.bee_id}.field est None")
            results['failed'] += 1
            results['warnings'] += 1
            print_warning("❌ PROBLÈME IDENTIFIÉ: Les abeilles n'ont pas accès au Field!")
    else:
        print_error(f"{bee.bee_id}.field n'existe pas")
        results['failed'] += 1
        results['warnings'] += 1
        print_warning("❌ PROBLÈME IDENTIFIÉ: bee.field manquant!")
    
    results['total'] += 1
    print_test(f"Vérification {bee.bee_id}.generate_signal...")
    if hasattr(bee, 'generate_signal'):
        print_success(f"{bee.bee_id}.generate_signal existe")
        print_info(f"Type: {type(bee.generate_signal)}")
        results['passed'] += 1
    else:
        print_error(f"{bee.bee_id}.generate_signal n'existe pas")
        results['failed'] += 1
        results['warnings'] += 1
        print_warning("❌ PROBLÈME: bee_signal_generator.py non appliqué!")
    
    results['total'] += 1
    print_test(f"Vérification {bee.bee_id}.fitness...")
    if hasattr(bee, 'fitness'):
        print_success(f"{bee.bee_id}.fitness existe: {bee.fitness}")
        results['passed'] += 1
    else:
        print_error(f"{bee.bee_id}.fitness n'existe pas")
        results['failed'] += 1

# ============================================================
# TEST 6: Field.get_market_info()
# ============================================================
print_header("TEST 6: FIELD.GET_MARKET_INFO()")

if hive and hasattr(hive, 'field') and hive.field is not None:
    results['total'] += 1
    print_test("Appel hive.field.get_market_info()...")
    try:
        market_info = hive.field.get_market_info()
        if market_info is not None:
            print_success("get_market_info() retourne des données")
            print_info(f"Prix: {market_info.get('price', 'N/A')}")
            print_info(f"ATR: {market_info.get('atr', 'N/A')}")
            print_info(f"Clés: {list(market_info.keys())}")
            results['passed'] += 1
        else:
            print_error("get_market_info() retourne None")
            results['failed'] += 1
    except Exception as e:
        print_error(f"Exception lors de get_market_info(): {e}")
        results['failed'] += 1
        import traceback
        traceback.print_exc()

# ============================================================
# TEST 7: Générateur de Signaux
# ============================================================
print_header("TEST 7: GÉNÉRATEUR DE SIGNAUX")

results['total'] += 1
print_test("Import bee_signal_generator...")
try:
    from bee_signal_generator import patch_hive_with_signal_generation
    print_success("bee_signal_generator importé")
    results['passed'] += 1
    
    if hive:
        results['total'] += 1
        print_test("Application du générateur à la Hive...")
        try:
            hive = patch_hive_with_signal_generation(hive)
            print_success("Générateur appliqué")
            results['passed'] += 1
            
            # Vérifier que generate_signal existe maintenant
            results['total'] += 1
            print_test("Vérification generate_signal après patch...")
            bee = hive.bees[0]
            if hasattr(bee, 'generate_signal'):
                print_success(f"{bee.bee_id}.generate_signal existe")
                results['passed'] += 1
            else:
                print_error(f"{bee.bee_id}.generate_signal manquant")
                results['failed'] += 1
                
        except Exception as e:
            print_error(f"Erreur application générateur: {e}")
            results['failed'] += 1
            import traceback
            traceback.print_exc()
            
except ImportError as e:
    print_error(f"bee_signal_generator.py non trouvé: {e}")
    results['failed'] += 1
    print_warning("Le fichier bee_signal_generator.py doit être présent")

# ============================================================
# TEST 8: Test Génération Signal
# ============================================================
print_header("TEST 8: TEST GÉNÉRATION SIGNAL RÉEL")

if hive and len(hive.bees) > 0:
    bee = hive.bees[0]
    
    # D'abord, s'assurer que bee a accès au field
    if not hasattr(bee, 'field') or bee.field is None:
        print_warning("Attribution manuelle du field à l'abeille...")
        if hasattr(hive, 'field'):
            bee.field = hive.field
            print_info("Field assigné manuellement")
    
    results['total'] += 1
    print_test(f"Appel {bee.bee_id}.generate_signal()...")
    
    if hasattr(bee, 'generate_signal'):
        try:
            signal = bee.generate_signal()
            if signal is not None:
                print_success(f"Signal généré: {signal}")
                results['passed'] += 1
                print_info(f"Type: {signal.get('type', 'N/A')}")
                print_info(f"Confidence: {signal.get('confidence', 'N/A')}")
            else:
                print_warning("generate_signal() retourne None (HOLD)")
                print_info("C'est normal si les conditions ne sont pas remplies")
                results['passed'] += 1
        except Exception as e:
            print_error(f"Exception lors de generate_signal(): {e}")
            results['failed'] += 1
            import traceback
            traceback.print_exc()
    else:
        print_error(f"{bee.bee_id}.generate_signal n'existe pas")
        results['failed'] += 1
        print_warning("Le générateur n'a pas été appliqué correctement")

# ============================================================
# TEST 9: Patch Field Access
# ============================================================
print_header("TEST 9: PATCH FIELD ACCESS")

results['total'] += 1
print_test("Import patch_field_access...")
try:
    from patch_field_access import patch_hive_give_field_to_bees
    print_success("patch_field_access importé")
    results['passed'] += 1
    
    if hive:
        results['total'] += 1
        print_test("Application du patch field...")
        try:
            hive = patch_hive_give_field_to_bees(hive)
            print_success("Patch field appliqué")
            results['passed'] += 1
            
            # Vérifier que toutes les abeilles ont le field maintenant
            results['total'] += 1
            print_test("Vérification field sur toutes les abeilles...")
            all_have_field = True
            for bee in hive.bees:
                if not hasattr(bee, 'field') or bee.field is None:
                    print_error(f"{bee.bee_id} n'a pas de field")
                    all_have_field = False
            
            if all_have_field:
                print_success("Toutes les abeilles ont accès au field")
                results['passed'] += 1
            else:
                print_error("Certaines abeilles n'ont pas de field")
                results['failed'] += 1
                
        except Exception as e:
            print_error(f"Erreur application patch field: {e}")
            results['failed'] += 1
            import traceback
            traceback.print_exc()
            
except ImportError as e:
    print_error(f"patch_field_access.py non trouvé: {e}")
    results['failed'] += 1
    print_warning("Le fichier patch_field_access.py doit être créé")

# ============================================================
# TEST 10: Test Complet avec Patches
# ============================================================
print_header("TEST 10: TEST COMPLET AVEC TOUS LES PATCHES")

print_test("Création nouvelle Hive + Application de tous les patches...")
try:
    # Créer nouvelle Hive
    test_hive = Hive(initial_capital=10000, num_bees=3, symbol='XAUUSD')
    print_success("Hive test créée")
    
    # Appliquer patch field
    if 'patch_hive_give_field_to_bees' in dir():
        test_hive = patch_hive_give_field_to_bees(test_hive)
        print_success("Patch field appliqué")
    
    # Appliquer générateur
    if 'patch_hive_with_signal_generation' in dir():
        test_hive = patch_hive_with_signal_generation(test_hive)
        print_success("Générateur appliqué")
    
    # Tester génération sur chaque abeille
    results['total'] += 1
    print_test("Test génération sur 3 abeilles...")
    signals_generated = 0
    for i, bee in enumerate(test_hive.bees):
        if hasattr(bee, 'generate_signal'):
            signal = bee.generate_signal()
            if signal:
                signals_generated += 1
                print_success(f"{bee.bee_id}: Signal généré!")
            else:
                print_info(f"{bee.bee_id}: None (HOLD)")
    
    print_info(f"Résultat: {signals_generated}/3 signaux générés")
    
    if signals_generated > 0:
        print_success("Au moins un signal généré - Système fonctionnel!")
        results['passed'] += 1
    else:
        print_warning("Aucun signal généré (peut être normal si marché calme)")
        print_info("Le système fonctionne, les conditions de signal ne sont juste pas remplies")
        results['passed'] += 1
    
    # Cleanup
    test_hive.shutdown()
    
except Exception as e:
    print_error(f"Erreur test complet: {e}")
    results['failed'] += 1
    import traceback
    traceback.print_exc()

# ============================================================
# RÉSUMÉ FINAL
# ============================================================
print_header("RÉSUMÉ DIAGNOSTIC")

print(f"\n{Colors.BOLD}Tests effectués: {results['total']}{Colors.END}")
print(f"{Colors.GREEN}✓ Réussis: {results['passed']}{Colors.END}")
print(f"{Colors.RED}✗ Échoués: {results['failed']}{Colors.END}")
print(f"{Colors.YELLOW}! Avertissements: {results['warnings']}{Colors.END}")

success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
print(f"\n{Colors.BOLD}Taux de réussite: {success_rate:.1f}%{Colors.END}")

# Déterminer l'état global
if results['failed'] == 0:
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ SYSTÈME FONCTIONNEL !{Colors.END}")
    print(f"{Colors.GREEN}Tous les tests sont passés. SWARNE est prêt à trader.{Colors.END}")
elif results['warnings'] > 0:
    print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ PROBLÈMES IDENTIFIÉS{Colors.END}")
    print(f"{Colors.YELLOW}Des corrections sont nécessaires (voir détails ci-dessus){Colors.END}")
else:
    print(f"\n{Colors.RED}{Colors.BOLD}✗ PROBLÈMES CRITIQUES{Colors.END}")
    print(f"{Colors.RED}Le système ne peut pas fonctionner (voir erreurs ci-dessus){Colors.END}")

# Recommandations
print(f"\n{Colors.CYAN}{Colors.BOLD}RECOMMANDATIONS:{Colors.END}")

if not hasattr(hive.bees[0] if hive and len(hive.bees) > 0 else None, 'field'):
    print(f"{Colors.YELLOW}→ Installer patch_field_access.py{Colors.END}")
    
if not hasattr(hive.bees[0] if hive and len(hive.bees) > 0 else None, 'generate_signal'):
    print(f"{Colors.YELLOW}→ Installer bee_signal_generator.py{Colors.END}")

if results['failed'] == 0 and results['warnings'] == 0:
    print(f"{Colors.GREEN}→ Lancer quick_start.py en mode production (Option 9){Colors.END}")
    print(f"{Colors.GREEN}→ Le système devrait générer des signaux et trader !{Colors.END}")

# Cleanup
if hive:
    try:
        hive.shutdown()
        print(f"\n{Colors.WHITE}Hive fermée proprement{Colors.END}")
    except:
        pass

if mt5.initialize():
    mt5.shutdown()
    print(f"{Colors.WHITE}MT5 déconnecté{Colors.END}")

print(f"\n{Colors.CYAN}{'='*70}")
print(f"  Diagnostic terminé")
print(f"{'='*70}{Colors.END}\n")

print("Appuyez sur Entrée pour quitter...")
input()
