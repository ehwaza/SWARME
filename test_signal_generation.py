"""
🧪 SWARNE - Test Direct Génération de Signaux
Script pour tester si les abeilles peuvent générer des signaux

Ce script crée une Hive, applique le générateur, et teste directement la génération
"""

import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('SWARNE.SignalTest')

print("\n" + "="*60)
print("🧪 TEST DIRECT GÉNÉRATION DE SIGNAUX")
print("="*60 + "\n")

try:
    # 1. Créer une Hive
    print("1️⃣ Création de la Hive...")
    from swarne_ultimate import Hive
    hive = Hive(initial_capital=12077.91, num_bees=5, symbol='XAUUSD')
    print(f"✅ Hive créée: {len(hive.bees)} abeilles\n")
    
    # 1.5 Vérifier et donner accès au Field
    print("1️⃣.5 Vérification du Field...")
    field_ok = False
    if hasattr(hive, 'field'):
        print(f"✅ Hive.field existe")
        
        # Donner le field à chaque abeille
        for bee in hive.bees:
            if not hasattr(bee, 'field') or bee.field is None:
                bee.field = hive.field
                print(f"   → {bee.bee_id}: field assigné")
        
        field_ok = True
    else:
        print(f"❌ Hive.field n'existe pas !")
    print()
    
    # 2. Appliquer le générateur
    print("2️⃣ Application du générateur de signaux...")
    from bee_signal_generator import patch_hive_with_signal_generation
    hive = patch_hive_with_signal_generation(hive)
    print("✅ Générateur appliqué\n")
    
    # 3. Tester chaque abeille
    print("3️⃣ Test de génération (10 tentatives par abeille):\n")
    
    total_signals = 0
    
    for bee in hive.bees:
        print(f"🐝 {bee.bee_id} (Type: {bee.bee_type}):")
        signals_count = 0
        
        for i in range(10):
            try:
                signal = bee.generate_signal()
                
                if signal:
                    signals_count += 1
                    total_signals += 1
                    print(f"   Tentative {i+1}: ✅ {signal['type']} (confidence: {signal['confidence']:.2%})")
                else:
                    print(f"   Tentative {i+1}: ➖ None (HOLD)")
            
            except Exception as e:
                print(f"   Tentative {i+1}: ❌ ERROR: {e}")
        
        print(f"   → {signals_count}/10 signaux générés\n")
    
    # 4. Résumé
    print("="*60)
    print("📊 RÉSUMÉ")
    print("="*60 + "\n")
    
    print(f"Abeilles testées: {len(hive.bees)}")
    print(f"Signaux générés au total: {total_signals}")
    print(f"Taux de génération: {total_signals/(len(hive.bees)*10)*100:.1f}%\n")
    
    if total_signals == 0:
        print("❌ PROBLÈME CRITIQUE: Aucun signal généré !")
        print("\n🔍 DIAGNOSTIC:")
        print("  Le générateur est appliqué mais ne génère rien.")
        print("  Raisons possibles:")
        print("  1. field.get_market_info() retourne None")
        print("  2. Toutes les conditions retournent HOLD")
        print("  3. Bug dans la logique du générateur")
        
        # Test du field
        print("\n🔬 TEST DU FIELD:")
        bee = hive.bees[0]
        if hasattr(bee, 'field'):
            print(f"  ✅ bee.field existe")
            market_data = bee.field.get_market_info()
            if market_data:
                print(f"  ✅ market_data récupéré")
                print(f"     Prix: {market_data.get('price', 'N/A')}")
                print(f"     ATR: {market_data.get('atr', 'N/A')}")
                print(f"     Close prices: {len(market_data.get('close_prices', []))} barres")
            else:
                print(f"  ❌ market_data est None !")
        else:
            print(f"  ❌ bee.field n'existe pas !")
    
    else:
        print(f"✅ {total_signals} signaux générés !")
        print("✅ Le générateur fonctionne !")
        print("\n💡 CONCLUSION:")
        print("  Le générateur fonctionne en test direct.")
        print("  Le problème est dans swarne_ultimate.py :")
        print("  → Le cycle ne fait pas appel à generate_signal()")
        print("  → Ou il l'appelle d'une manière qui ne fonctionne pas")
    
    # 5. Nettoyage
    hive.shutdown()
    
    print("\n✅ Test terminé\n")
    
except ImportError as e:
    print(f"❌ Erreur import: {e}")
    print("   Vérifiez que tous les fichiers sont présents\n")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

input("\nAppuyez sur Entrée pour quitter...")
