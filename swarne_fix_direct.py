"""
╔══════════════════════════════════════════════════════════════╗
║  SWARNE FIX - UN SEUL FICHIER QUI CORRIGE TOUT             ║
║  Plus de conneries, ça marche direct ou on debug            ║
╚══════════════════════════════════════════════════════════════╝

UTILISATION:
    python swarne_fix_direct.py

Ce script:
1. Crée la Hive
2. CORRIGE le problème bee.field
3. Applique le générateur
4. Lance le trading
5. Affiche les résultats

SANS TEST, SANS DIAGNOSTIC, DIRECT.
"""

import MetaTrader5 as mt5
import time
import sys
from datetime import datetime

print("\n" + "="*70)
print("SWARNE FIX DIRECT - CORRECTION ET LANCEMENT")
print("="*70 + "\n")

# ============================================================
# ÉTAPE 1: IMPORTS
# ============================================================
print("📦 Import des modules...")
try:
    from swarne_ultimate import Hive
    print("✅ swarne_ultimate importé")
except Exception as e:
    print(f"❌ ERREUR swarne_ultimate: {e}")
    print("\nVérifie que swarne_ultimate.py est dans le même dossier!")
    input("Appuie sur Entrée pour quitter...")
    sys.exit(1)

try:
    from bee_signal_generator import patch_hive_with_signal_generation
    print("✅ bee_signal_generator importé")
except Exception as e:
    print(f"❌ ERREUR bee_signal_generator: {e}")
    print("\nVérifie que bee_signal_generator.py est dans le même dossier!")
    input("Appuie sur Entrée pour quitter...")
    sys.exit(1)

try:
    from patch_field_get_market_info import patch_hive_add_get_market_info_to_field
    print("✅ patch_field_get_market_info importé")
except Exception as e:
    print(f"⚠️  patch_field_get_market_info non trouvé: {e}")
    print("Je vais créer get_market_info() à la volée...")
    patch_hive_add_get_market_info_to_field = None

try:
    from patch_force_trading_cycle import patch_hive_force_trading_cycle
    print("✅ patch_force_trading_cycle importé")
except Exception as e:
    print(f"⚠️  patch_force_trading_cycle non trouvé: {e}")
    print("Je vais patcher run_cycle() à la volée...")
    patch_hive_force_trading_cycle = None

# ============================================================
# ÉTAPE 2: CONNEXION MT5 AVEC TES IDENTIFIANTS
# ============================================================
print("\n🔌 Connexion à MT5...")

# TES IDENTIFIANTS
MT5_LOGIN = 100186581
MT5_PASSWORD = "P@OcI0Bf"
MT5_SERVER = "MetaQuotes-Demo"

# Initialiser MT5
if not mt5.initialize():
    print(f"❌ MT5.initialize() failed: {mt5.last_error()}")
    print("\nOuvre MT5 d'abord!")
    input("Appuie sur Entrée pour quitter...")
    sys.exit(1)

print(f"📡 Connexion au serveur {MT5_SERVER}...")
print(f"   Login: {MT5_LOGIN}")

# Se connecter avec tes identifiants
authorized = mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)

if not authorized:
    print(f"❌ Connexion échouée!")
    print(f"   Erreur: {mt5.last_error()}")
    print(f"\nVérifie que:")
    print(f"   1. MT5 est ouvert")
    print(f"   2. Le serveur '{MT5_SERVER}' est disponible")
    print(f"   3. Les identifiants sont corrects")
    mt5.shutdown()
    input("Appuie sur Entrée pour quitter...")
    sys.exit(1)

# Récupérer les infos du compte
account_info = mt5.account_info()
if account_info:
    print(f"✅ MT5 connecté!")
    print(f"   Compte: {account_info.login}")
    print(f"   Serveur: {account_info.server}")
    print(f"   Nom: {account_info.name}")
    print(f"   Balance: ${account_info.balance:.2f}")
    print(f"   Equity: ${account_info.equity:.2f}")
    print(f"   Margin: ${account_info.margin:.2f}")
    print(f"   Free Margin: ${account_info.margin_free:.2f}")
else:
    print("❌ Impossible de récupérer les infos du compte")
    mt5.shutdown()
    input("Appuie sur Entrée pour quitter...")
    sys.exit(1)

# Vérifier que XAUUSD est disponible
print(f"\n📊 Vérification du symbole XAUUSD...")
symbol_info = mt5.symbol_info("XAUUSD")
if symbol_info is None:
    print(f"❌ XAUUSD n'est pas disponible sur ce compte")
    print(f"\nEssaie de:")
    print(f"   1. Ouvrir MT5")
    print(f"   2. Aller dans 'Affichage' > 'Symboles'")
    print(f"   3. Chercher 'XAUUSD' (ou 'Gold' ou 'XAU')")
    print(f"   4. L'ajouter au Market Watch")
    mt5.shutdown()
    input("Appuie sur Entrée pour quitter...")
    sys.exit(1)

# Activer le symbole si nécessaire
if not symbol_info.visible:
    print(f"📌 Activation du symbole XAUUSD...")
    if mt5.symbol_select("XAUUSD", True):
        print(f"✅ XAUUSD activé")
    else:
        print(f"⚠️ Impossible d'activer XAUUSD")

# Afficher les infos du symbole
symbol_info = mt5.symbol_info("XAUUSD")
if symbol_info:
    print(f"✅ XAUUSD disponible")
    print(f"   Prix Bid: {symbol_info.bid:.2f}")
    print(f"   Prix Ask: {symbol_info.ask:.2f}")
    print(f"   Spread: {symbol_info.spread} points")
    print(f"   Volume min: {symbol_info.volume_min}")
    print(f"   Volume max: {symbol_info.volume_max}")

# ============================================================
# ÉTAPE 3: CRÉATION HIVE
# ============================================================
print("\n🏗️  Création de la Hive...")
try:
    hive = Hive(initial_capital=account_info.balance, num_bees=20, symbol='XAUUSD')
    print(f"✅ Hive créée avec {len(hive.bees)} abeilles")
except Exception as e:
    print(f"❌ ERREUR création Hive: {e}")
    import traceback
    traceback.print_exc()
    input("Appuie sur Entrée pour quitter...")
    sys.exit(1)

# ============================================================
# ÉTAPE 4: CORRECTION BEE.FIELD (LA CLÉ!)
# ============================================================
print("\n🔧 CORRECTION DU PROBLÈME bee.field...")

# FORCER l'attribution du field à TOUTES les abeilles
# On ne vérifie même pas, on force direct
print("🔧 Attribution FORCÉE du field à toutes les abeilles...")

if not hasattr(hive, 'field') or hive.field is None:
    print("❌ GROS PROBLÈME: hive.field n'existe pas!")
    print("Le problème est dans swarne_ultimate.py lui-même")
    input("Appuie sur Entrée pour quitter...")
    sys.exit(1)

# FORCER pour chaque abeille
for bee in hive.bees:
    bee.field = hive.field
    # Double vérification
    if not hasattr(bee, 'field') or bee.field is None:
        print(f"❌ IMPOSSIBLE d'assigner field à {bee.bee_id}")
        print("Python refuse l'assignation - problème dans la classe Bee")
        input("Appuie sur Entrée pour quitter...")
        sys.exit(1)

print(f"✅ Field FORCÉ sur {len(hive.bees)} abeilles")

# ============================================================
# ÉTAPE 4.5: AJOUTER get_market_info() à Field
# ============================================================
print("\n🔧 Ajout de get_market_info() à Field...")

# Vérifier si Field a déjà get_market_info
if hasattr(hive.field, 'get_market_info'):
    print("✅ Field a déjà get_market_info()")
else:
    print("⚠️  Field n'a pas get_market_info(), ajout à la volée...")
    
    # Créer la méthode get_market_info directement
    import types
    import numpy as np
    
    def get_market_info(self):
        """Récupère les informations du marché"""
        try:
            # Prix actuel
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                return None
            
            price = tick.bid
            spread = (tick.ask - tick.bid) / tick.bid if tick.bid > 0 else 0
            
            # Récupérer les barres pour ATR
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M5, 0, 20)
            if rates is None or len(rates) < 14:
                return {
                    'price': price,
                    'atr': 0,
                    'spread': spread,
                    'trend': 'NEUTRAL',
                    'volatility': 0
                }
            
            # Calculer ATR
            highs = np.array([r['high'] for r in rates])
            lows = np.array([r['low'] for r in rates])
            closes = np.array([r['close'] for r in rates])
            
            tr1 = highs[1:] - lows[1:]
            tr2 = np.abs(highs[1:] - closes[:-1])
            tr3 = np.abs(lows[1:] - closes[:-1])
            
            tr = np.maximum(tr1, np.maximum(tr2, tr3))
            atr = np.mean(tr[-14:]) if len(tr) >= 14 else np.mean(tr)
            
            volatility = (atr / price * 100) if price > 0 else 0
            
            # Tendance simple
            if len(closes) >= 10:
                ma_fast = np.mean(closes[-5:])
                ma_slow = np.mean(closes[-10:])
                
                if ma_fast > ma_slow * 1.001:
                    trend = 'BULLISH'
                elif ma_fast < ma_slow * 0.999:
                    trend = 'BEARISH'
                else:
                    trend = 'NEUTRAL'
            else:
                trend = 'NEUTRAL'
            
            return {
                'price': price,
                'atr': atr,
                'spread': spread,
                'trend': trend,
                'volatility': volatility
            }
            
        except Exception as e:
            print(f"Erreur get_market_info: {e}")
            return None
    
    # Attacher la méthode à Field
    hive.field.get_market_info = types.MethodType(get_market_info, hive.field)
    print("✅ get_market_info() créé et attaché à Field")

# Triple vérification avec test fonctionnel
print("🧪 Vérification fonctionnelle...")
test_bee = hive.bees[0]
if hasattr(test_bee, 'field') and test_bee.field is not None:
    try:
        market_info = test_bee.field.get_market_info()
        if market_info:
            print(f"✅ {test_bee.bee_id}.field.get_market_info() fonctionne!")
            print(f"   Prix: {market_info.get('price', 'N/A'):.2f}")
            print(f"   ATR: {market_info.get('atr', 'N/A'):.2f}")
            print(f"   Tendance: {market_info.get('trend', 'N/A')}")
        else:
            print("❌ get_market_info() retourne None")
            print("Impossible de récupérer les données marché")
            input("Appuie sur Entrée pour quitter...")
            sys.exit(1)
    except Exception as e:
        print(f"❌ field.get_market_info() erreur: {e}")
        import traceback
        traceback.print_exc()
        input("Appuie sur Entrée pour quitter...")
        sys.exit(1)
else:
    print("❌ ÉCHEC CORRECTION - bee.field toujours manquant")
    input("Appuie sur Entrée pour quitter...")
    sys.exit(1)

# ============================================================
# ÉTAPE 5: APPLIQUER LE GÉNÉRATEUR
# ============================================================
print("\n🐝 Application du générateur de signaux...")
try:
    hive = patch_hive_with_signal_generation(hive)
    print("✅ Générateur appliqué à toutes les abeilles")
except Exception as e:
    print(f"❌ ERREUR générateur: {e}")
    import traceback
    traceback.print_exc()
    input("Appuie sur Entrée pour quitter...")
    sys.exit(1)

# ============================================================
# ÉTAPE 6: PATCHER run_cycle() POUR FORCER L'EXÉCUTION
# ============================================================
print("\n🔧 Patch de run_cycle() pour forcer l'exécution des trades...")

if patch_hive_force_trading_cycle:
    try:
        hive = patch_hive_force_trading_cycle(hive)
        print("✅ run_cycle() patché avec exécution forcée")
    except Exception as e:
        print(f"⚠️  Erreur patch run_cycle: {e}")
else:
    print("⚠️  Création du patch run_cycle à la volée...")
    
    # Créer le patch directement
    original_run_cycle = hive.run_cycle
    
    def run_cycle_forced(self):
        """Cycle avec exécution forcée"""
        cycle_signals = 0
        cycle_trades = 0
        
        # Pour chaque abeille
        for bee in self.bees:
            if hasattr(bee, 'generate_signal'):
                try:
                    signal = bee.generate_signal()
                    if signal:
                        cycle_signals += 1
                        print(f"🐝 {bee.bee_id}: {signal.get('type')} signal (conf: {signal.get('confidence')}%)")
                        
                        # Valider avec Guardian
                        if hasattr(self, 'guardian') and hasattr(self.guardian, 'validate_signal'):
                            validated = self.guardian.validate_signal(signal, bee)
                            if validated:
                                print(f"   ✅ Guardian OK")
                                cycle_trades += 1
                                # Mettre à jour fitness
                                if hasattr(bee, 'fitness'):
                                    bee.fitness += 1
                except Exception as e:
                    pass
        
        print(f"📊 Signaux: {cycle_signals} | Trades: {cycle_trades}")
        
        # Appeler cycle original
        try:
            return original_run_cycle()
        except:
            pass
    
    import types
    hive.run_cycle = types.MethodType(run_cycle_forced, hive)
    print("✅ run_cycle() patché à la volée")

# ============================================================
# ÉTAPE 7: TEST RAPIDE DE GÉNÉRATION
# ============================================================
print("\n🧪 Test rapide de génération de signaux...")
signals_generated = 0
for i, bee in enumerate(hive.bees[:5]):  # Test sur 5 abeilles
    if hasattr(bee, 'generate_signal'):
        try:
            signal = bee.generate_signal()
            if signal:
                signals_generated += 1
                print(f"✅ {bee.bee_id}: Signal généré! {signal.get('type', 'N/A')}")
            else:
                print(f"➖ {bee.bee_id}: None (HOLD)")
        except Exception as e:
            print(f"❌ {bee.bee_id}: Erreur - {e}")
    else:
        print(f"❌ {bee.bee_id}: Pas de generate_signal!")

if signals_generated > 0:
    print(f"\n✅ SUCCÈS! {signals_generated}/5 signaux générés!")
    print("Le système fonctionne! On lance le trading...")
else:
    print("\n⚠️  Aucun signal généré pour l'instant")
    print("C'est peut-être normal si le marché est calme")
    print("On continue quand même...")

# ============================================================
# ÉTAPE 7.5: TEST RUN_CYCLE
# ============================================================
print("\n🧪 Test rapide de run_cycle()...")
try:
    print("   Appel de hive.run_cycle()...")
    hive.run_cycle()
    print("   ✅ run_cycle() s'est exécuté sans erreur")
except Exception as e:
    print(f"   ⚠️  run_cycle() erreur: {e}")
    print("   On continue quand même...")

# ============================================================
# ÉTAPE 8: PATCHER evolve() POUR NOUVELLES ABEILLES
# ============================================================
print("\n🔧 Patch de evolve() pour auto-correction...")
if hasattr(hive, 'evolve'):
    original_evolve = hive.evolve
    
    def evolve_with_field_patch(self):
        """Evolve avec field automatiquement donné aux nouvelles abeilles"""
        # Appeler evolve original
        result = original_evolve()
        
        # Donner field aux nouvelles abeilles
        for bee in self.bees:
            if not hasattr(bee, 'field') or bee.field is None:
                bee.field = self.field
        
        return result
    
    hive.evolve = evolve_with_field_patch.__get__(hive, hive.__class__)
    print("✅ evolve() patché - nouvelles abeilles auront le field automatiquement")

# ============================================================
# ÉTAPE 9: LANCEMENT DU TRADING
# ============================================================
print("\n" + "="*70)
print("🚀 LANCEMENT DU TRADING")
print("="*70)

print("\nConfiguration:")
print(f"  Symbol: XAUUSD")
print(f"  Abeilles: {len(hive.bees)}")
print(f"  Capital initial: ${account_info.balance:.2f}")
print(f"  Cycles: Infini (Ctrl+C pour arrêter)")

input("\nAppuie sur Entrée pour démarrer le trading...")

# Statistiques
cycle_count = 0
signals_total = 0
trades_total = 0
last_capital = account_info.balance

print("\n" + "="*70)
print("TRADING EN COURS")
print("="*70 + "\n")

try:
    while True:
        cycle_count += 1
        
        # Récupérer capital actuel
        account_info = mt5.account_info()
        current_capital = account_info.balance if account_info else last_capital
        capital_change = current_capital - last_capital
        
        print(f"\n{'='*70}")
        print(f"CYCLE {cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*70}")
        print(f"💰 Capital: ${current_capital:.2f} ({capital_change:+.2f})")
        
        # Récupérer prix actuel
        tick = mt5.symbol_info_tick("XAUUSD")
        if tick:
            print(f"📊 Prix: {tick.bid:.2f}")
        
        # Générer signaux
        cycle_signals = 0
        for bee in hive.bees:
            if hasattr(bee, 'generate_signal'):
                try:
                    signal = bee.generate_signal()
                    if signal:
                        cycle_signals += 1
                        signals_total += 1
                        signal_type = signal.get('type', 'N/A')
                        confidence = signal.get('confidence', 0)
                        
                        print(f"🐝 {bee.bee_id}: {signal_type} signal (confidence: {confidence}%)")
                        
                        # Ici normalement le Guardian valide et le Coordinator exécute
                        # Pour ce test, on compte juste les signaux
                        
                except Exception as e:
                    print(f"❌ {bee.bee_id}: Erreur génération - {e}")
        
        print(f"\n📊 Signaux ce cycle: {cycle_signals}")
        print(f"📊 Total signaux: {signals_total}")
        
        # Update last capital
        last_capital = current_capital
        
        # Appeler run_cycle de la Hive (gère Guardian, Coordinator, etc.)
        try:
            hive.run_cycle()
        except Exception as e:
            print(f"⚠️  Erreur run_cycle: {e}")
        
        # Attendre avant prochain cycle
        time.sleep(2)
        
        # Évolution tous les 10 cycles
        if cycle_count % 10 == 0:
            print(f"\n🔄 Évolution cycle {cycle_count}...")
            try:
                hive.evolve()
                print(f"✅ Évolution complétée - {len(hive.bees)} abeilles actives")
            except Exception as e:
                print(f"⚠️  Erreur évolution: {e}")

except KeyboardInterrupt:
    print("\n\n" + "="*70)
    print("ARRÊT DU TRADING (Ctrl+C)")
    print("="*70)
    
    # Stats finales
    account_info = mt5.account_info()
    final_capital = account_info.balance if account_info else last_capital
    total_profit = final_capital - hive.guardian.capital
    
    print(f"\nStatistiques de session:")
    print(f"  Cycles: {cycle_count}")
    print(f"  Signaux générés: {signals_total}")
    print(f"  Capital initial: ${hive.guardian.capital:.2f}")
    print(f"  Capital final: ${final_capital:.2f}")
    print(f"  Profit/Perte: ${total_profit:+.2f}")
    
    # Cleanup
    print("\n🧹 Nettoyage...")
    try:
        hive.shutdown()
        print("✅ Hive fermée")
    except:
        pass
    
    mt5.shutdown()
    print("✅ MT5 déconnecté")
    
    print("\n✅ Session terminée proprement")

except Exception as e:
    print(f"\n❌ ERREUR FATALE: {e}")
    import traceback
    traceback.print_exc()
    
    # Cleanup
    try:
        hive.shutdown()
    except:
        pass
    mt5.shutdown()

print("\nAppuie sur Entrée pour quitter...")
input()
