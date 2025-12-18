"""
🔍 SWARNE - Diagnostic Génération de Signaux
Tester pourquoi les abeilles ne génèrent pas de signaux

UTILISATION:
- Double-clic depuis Windows : OK ✅
- Lancement depuis terminal : OK ✅
- La fenêtre reste ouverte jusqu'à ce que vous appuyiez sur Entrée
"""

import sys
import os
import logging
import traceback

# Changer le dossier de travail
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
except:
    pass

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Fonction principale du diagnostic"""
    print("\n" + "="*60)
    print("🔍 DIAGNOSTIC GÉNÉRATION DE SIGNAUX")
    print("="*60 + "\n")
    print("📂 Dossier de travail:", os.getcwd())
    print()

def main():
    """Fonction principale du diagnostic"""
    print("\n" + "="*60)
    print("🔍 DIAGNOSTIC GÉNÉRATION DE SIGNAUX")
    print("="*60 + "\n")
    print("📂 Dossier de travail:", os.getcwd())
    print()

    try:
        # 1. Importer la Hive
        print("📦 Import de swarne_ultimate...")
        from swarne_ultimate import Hive
        print("✅ Import réussi\n")
        
        # 2. Créer une Hive de test
        print("🏗️  Création d'une Hive de test...")
        hive = Hive(initial_capital=10000, num_bees=5, symbol='XAUUSD')
        print(f"✅ Hive créée: {len(hive.bees)} abeilles\n")
        
        # 2.5 Appliquer le générateur de signaux
        print("🐝 Application du générateur de signaux...")
        try:
            from bee_signal_generator import patch_hive_with_signal_generation
            hive = patch_hive_with_signal_generation(hive)
            print("✅ Générateur appliqué !\n")
            generator_applied = True
        except ImportError:
            print("⚠️  bee_signal_generator.py non trouvé")
            print("   Les abeilles n'auront pas de méthode generate_signal()")
            print("   Téléchargez bee_signal_generator.py\n")
            generator_applied = False
        except Exception as e:
            print(f"⚠️  Erreur générateur: {e}\n")
            generator_applied = False
        
        # 3. Tester chaque abeille
        print("🐝 Test de génération de signaux:\n")
        
        signals_generated = 0
        
        for i, bee in enumerate(hive.bees):
            print(f"Abeille {i+1}/{len(hive.bees)}: {bee.bee_id} (Type: {bee.bee_type})")
            
            try:
                # Vérifier si la méthode existe
                if not hasattr(bee, 'generate_signal'):
                    print(f"  ❌ Pas de méthode generate_signal() !")
                    continue
                
                # Essayer de générer un signal
                signal = bee.generate_signal()
                
                if signal is None:
                    print(f"  ❌ Signal = None")
                    print(f"     Fitness: {bee.fitness}")
                    
                    # Analyser pourquoi
                    if hasattr(bee, 'field'):
                        market_data = bee.field.get_market_info()
                        if market_data:
                            print(f"     Prix: {market_data.get('price', 'N/A')}")
                            print(f"     ATR: {market_data.get('atr', 'N/A')}")
                        else:
                            print(f"     ⚠️  Pas de données marché")
                    
                else:
                    print(f"  ✅ Signal généré !")
                    print(f"     Type: {signal.get('type', 'N/A')}")
                    print(f"     Confidence: {signal.get('confidence', 0):.2%}")
                    print(f"     Entry: {signal.get('entry_price', 'N/A')}")
                    print(f"     SL: {signal.get('stop_loss', 'N/A')}")
                    print(f"     TP: {signal.get('take_profit', 'N/A')}")
                    signals_generated += 1
                    
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
            
            print()
        
        # 4. Résumé
        print("="*60)
        print("📊 RÉSUMÉ DU DIAGNOSTIC")
        print("="*60 + "\n")
        
        print(f"Abeilles testées: {len(hive.bees)}")
        print(f"Signaux générés: {signals_generated}")
        print(f"Taux de génération: {signals_generated/len(hive.bees)*100:.1f}%\n")
        
        if not generator_applied:
            print("⚠️  GÉNÉRATEUR NON APPLIQUÉ !")
            print("\n🔍 CAUSE:")
            print("  bee_signal_generator.py non trouvé dans le dossier")
            print("\n💡 SOLUTION:")
            print("  1. Télécharge bee_signal_generator.py")
            print("  2. Place-le dans C:\\Users\\Mathieu\\Documents\\SWARM\\")
            print("  3. Relance le diagnostic")
        elif signals_generated == 0:
            print("❌ PROBLÈME: Générateur appliqué mais aucun signal !")
            print("\n🔍 CAUSES POSSIBLES:")
            print("  1. Pas de données marché disponibles")
            print("  2. Conditions de marché ne génèrent pas de signal")
            print("  3. Bug dans la logique du générateur")
            print("\n💡 SOLUTION:")
            print("  → Envoie ce résultat à Claude pour analyse")
        else:
            print(f"✅ {signals_generated} signaux générés !")
            print("✅ Le générateur fonctionne correctement !")
            print("\n🚀 PROCHAINE ÉTAPE:")
            print("  Lance le mode production (option 9)")
            print("  Les abeilles vont commencer à trader !")
        
        # 5. Tester le Guardian
        print("\n" + "="*60)
        print("🛡️  TEST DU GUARDIAN")
        print("="*60 + "\n")
        
        if signals_generated > 0:
            # Prendre le premier signal généré
            for bee in hive.bees:
                signal = bee.generate_signal()
                if signal:
                    print(f"Signal test: {signal.get('type')} à {signal.get('confidence', 0):.2%}")
                    
                    # Tester validation
                    validated = hive.guardian.validate_trade(signal)
                    
                    if validated:
                        print("✅ Guardian ACCEPTE le signal")
                    else:
                        print("❌ Guardian REFUSE le signal")
                        print("\n🔍 Raisons possibles:")
                        print(f"  - Confidence trop faible (< seuil)")
                        print(f"  - Capital insuffisant")
                        print(f"  - Conditions Guardian trop strictes")
                    
                    break
        else:
            print("⚠️  Impossible de tester (aucun signal généré)")
        
        # 6. Afficher le code de generate_signal
        print("\n" + "="*60)
        print("📝 CODE DE GENERATE_SIGNAL")
        print("="*60 + "\n")
        
        if len(hive.bees) > 0:
            bee = hive.bees[0]
            if hasattr(bee, 'generate_signal'):
                import inspect
                try:
                    source = inspect.getsource(bee.generate_signal)
                    print(source)
                except:
                    print("⚠️  Impossible de récupérer le code source")
        
        print("\n✅ Diagnostic terminé\n")
        
        # Nettoyage
        try:
            hive.shutdown()
        except:
            pass
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        print("   Assurez-vous d'être dans le bon dossier")
        print(f"   Dossier actuel: {os.getcwd()}\n")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("\n📋 Traceback complet:")
        traceback.print_exc()
        return False


if __name__ == '__main__':
    try:
        # Lancer le diagnostic
        success = main()
        
        # Message de fin
        print("\n" + "="*60)
        if success:
            print("✅ Diagnostic complété avec succès")
        else:
            print("❌ Diagnostic terminé avec erreurs")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Diagnostic interrompu par l'utilisateur\n")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}\n")
        traceback.print_exc()
    finally:
        # IMPORTANT: Garder la fenêtre ouverte
        print("\n💡 Appuyez sur Entrée pour fermer cette fenêtre...")
        try:
            input()
        except:
            pass
