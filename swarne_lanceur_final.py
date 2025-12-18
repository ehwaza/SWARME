"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  SWARNE - LANCEUR TOUT-EN-UN - VERSION FINALE               ║
║                                                              ║
║  Ce fichier fait TOUT :                                     ║
║  1. Connexion MT5                                           ║
║  2. Création Hive                                           ║
║  3. Corrections automatiques (field, get_market_info, etc)  ║
║  4. Lancement trading                                       ║
║                                                              ║
║  TU LANCES, ÇA MARCHE.                                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

UTILISATION:
    python swarne_lanceur_final.py
"""

import MetaTrader5 as mt5
import numpy as np
import time
import sys
import types
from datetime import datetime

print("\n" + "="*70)
print("🐝 SWARNE - LANCEUR TOUT-EN-UN")
print("="*70 + "\n")

# ============================================================
# CONFIGURATION
# ============================================================
MT5_LOGIN = 100186581
MT5_PASSWORD = "P@OcI0Bf"
MT5_SERVER = "MetaQuotes-Demo"
SYMBOL = "XAUUSD"
NUM_BEES = 20

# ============================================================
# ÉTAPE 1: IMPORTS
# ============================================================
print("📦 Import des modules...")
try:
    from swarne_ultimate import Hive
    print("✅ swarne_ultimate")
except:
    print("❌ swarne_ultimate.py manquant!")
    input("Appuie sur Entrée...")
    sys.exit(1)

try:
    from bee_signal_generator import patch_hive_with_signal_generation
    print("✅ bee_signal_generator")
except:
    print("⚠️  bee_signal_generator.py manquant, création à la volée...")
    patch_hive_with_signal_generation = None

# ============================================================
# ÉTAPE 2: CONNEXION MT5
# ============================================================
print("\n🔌 Connexion à MT5...")

if not mt5.initialize():
    print("❌ MT5.initialize() failed")
    input("Appuie sur Entrée...")
    sys.exit(1)

authorized = mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
if not authorized:
    print(f"❌ Connexion échouée: {mt5.last_error()}")
    mt5.shutdown()
    input("Appuie sur Entrée...")
    sys.exit(1)

account_info = mt5.account_info()
print(f"✅ Connecté: {account_info.name}")
print(f"   Balance: ${account_info.balance:.2f}")

# Vérifier symbole
symbol_info = mt5.symbol_info(SYMBOL)
if symbol_info is None:
    print(f"❌ {SYMBOL} indisponible")
    mt5.shutdown()
    input("Appuie sur Entrée...")
    sys.exit(1)

if not symbol_info.visible:
    mt5.symbol_select(SYMBOL, True)

print(f"✅ {SYMBOL} @ {symbol_info.bid:.2f}")

# ============================================================
# ÉTAPE 3: CRÉATION HIVE
# ============================================================
print(f"\n🏗️  Création Hive ({NUM_BEES} abeilles)...")
hive = Hive(initial_capital=account_info.balance, num_bees=NUM_BEES, symbol=SYMBOL)
print(f"✅ {len(hive.bees)} abeilles créées")

# ============================================================
# ÉTAPE 4: CORRECTION AUTOMATIQUE
# ============================================================
print("\n🔧 CORRECTIONS AUTOMATIQUES...")

# 4.1 - Donner field aux abeilles
print("   → bee.field...")
for bee in hive.bees:
    bee.field = hive.field
print("   ✅ field assigné")

# 4.2 - Créer get_market_info() dans Field
print("   → Field.get_market_info()...")
def get_market_info(self):
    """Récupère infos marché"""
    try:
        tick = mt5.symbol_info_tick(self.symbol)
        if not tick:
            return None
        
        price = tick.bid
        spread = (tick.ask - tick.bid) / tick.bid if tick.bid > 0 else 0
        
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M5, 0, 20)
        if rates is None or len(rates) < 14:
            return {
                'price': price,
                'atr': 0,
                'spread': spread,
                'trend': 'NEUTRAL',
                'volatility': 0
            }
        
        highs = np.array([r['high'] for r in rates])
        lows = np.array([r['low'] for r in rates])
        closes = np.array([r['close'] for r in rates])
        
        tr1 = highs[1:] - lows[1:]
        tr2 = np.abs(highs[1:] - closes[:-1])
        tr3 = np.abs(lows[1:] - closes[:-1])
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr = np.mean(tr[-14:]) if len(tr) >= 14 else np.mean(tr)
        
        volatility = (atr / price * 100) if price > 0 else 0
        
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
    except:
        return None

hive.field.get_market_info = types.MethodType(get_market_info, hive.field)
print("   ✅ get_market_info créé")

# 4.3 - Appliquer générateur de signaux
print("   → Générateur signaux...")
if patch_hive_with_signal_generation:
    hive = patch_hive_with_signal_generation(hive)
    print("   ✅ générateur appliqué")
else:
    print("   ⚠️  générateur non disponible")

# 4.4 - Patcher run_cycle pour EXÉCUTER les trades
print("   → run_cycle() patché...")
original_run_cycle = hive.run_cycle

def run_cycle_fixed(self):
    """Cycle avec exécution RÉELLE des signaux dans MT5"""
    
    cycle_signals = 0
    cycle_trades = 0
    
    # Pour chaque abeille
    for bee in self.bees:
        if hasattr(bee, 'generate_signal'):
            try:
                signal = bee.generate_signal()
                if signal:
                    cycle_signals += 1
                    sig_type = signal.get('type', 'N/A')
                    confidence = signal.get('confidence', 0)
                    price = signal.get('price', 0)
                    
                    # Valider avec Guardian
                    if confidence >= 60:
                        
                        # EXÉCUTER RÉELLEMENT dans MT5
                        try:
                            # Préparer l'ordre
                            symbol = self.field.symbol if hasattr(self, 'field') else SYMBOL
                            volume = 0.01  # Volume minimum
                            
                            # Type d'ordre
                            if sig_type == 'BUY':
                                order_type = mt5.ORDER_TYPE_BUY
                                price_exec = mt5.symbol_info_tick(symbol).ask
                            else:  # SELL
                                order_type = mt5.ORDER_TYPE_SELL
                                price_exec = mt5.symbol_info_tick(symbol).bid
                            
                            # Calculer SL/TP (simple : ±50 pips)
                            point = mt5.symbol_info(symbol).point
                            if sig_type == 'BUY':
                                sl = price_exec - 50 * 10 * point  # Gold = 10 points = 1 pip
                                tp = price_exec + 50 * 10 * point
                            else:
                                sl = price_exec + 50 * 10 * point
                                tp = price_exec - 50 * 10 * point
                            
                            # Créer la requête
                            request = {
                                "action": mt5.TRADE_ACTION_DEAL,
                                "symbol": symbol,
                                "volume": volume,
                                "type": order_type,
                                "price": price_exec,
                                "sl": sl,
                                "tp": tp,
                                "deviation": 20,
                                "magic": 234000,
                                "comment": f"SWARNE_{bee.bee_id}",
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_IOC,
                            }
                            
                            # ENVOYER L'ORDRE
                            result = mt5.order_send(request)
                            
                            if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                                cycle_trades += 1
                                
                                # Mettre à jour fitness
                                if hasattr(bee, 'fitness'):
                                    bee.fitness += 1
                                
                                # Log
                                if cycle_signals <= 3:
                                    print(f"   🐝 {bee.bee_id}: {sig_type} ({confidence}%) → Order #{result.order}")
                            else:
                                error = result.comment if result else "Unknown"
                                if cycle_signals <= 3:
                                    print(f"   ❌ {bee.bee_id}: {sig_type} FAILED - {error}")
                        
                        except Exception as e:
                            if cycle_signals <= 3:
                                print(f"   ❌ {bee.bee_id}: Error executing - {e}")
            except:
                pass
    
    if cycle_signals > 0:
        print(f"   📊 Cycle: {cycle_signals} signaux → {cycle_trades} trades exécutés")
    
    # Appeler cycle original
    try:
        return original_run_cycle()
    except:
        pass

hive.run_cycle = types.MethodType(run_cycle_fixed, hive)
print("   ✅ run_cycle patché")

# 4.5 - Patcher evolve pour auto-field
print("   → evolve() patché...")
if hasattr(hive, 'evolve'):
    original_evolve = hive.evolve
    
    def evolve_fixed(self):
        result = original_evolve()
        # Donner field aux nouvelles abeilles
        for bee in self.bees:
            if not hasattr(bee, 'field') or bee.field is None:
                bee.field = self.field
        return result
    
    hive.evolve = types.MethodType(evolve_fixed, hive)
    print("   ✅ evolve patché")

print("\n✅ TOUTES LES CORRECTIONS APPLIQUÉES")

# ============================================================
# ÉTAPE 5: TEST RAPIDE
# ============================================================
print("\n🧪 Test rapide...")
test_count = 0
for bee in hive.bees[:3]:
    if hasattr(bee, 'generate_signal'):
        try:
            sig = bee.generate_signal()
            if sig:
                test_count += 1
                print(f"   ✅ {bee.bee_id}: {sig.get('type')}")
        except:
            pass

if test_count > 0:
    print(f"\n✅ {test_count}/3 signaux générés - Système OK!")
else:
    print("\n⚠️  Aucun signal généré (marché calme?)")

# ============================================================
# ÉTAPE 6: LANCEMENT TRADING
# ============================================================
print("\n" + "="*70)
print("🚀 LANCEMENT TRADING")
print("="*70)
print(f"\nSymbol: {SYMBOL}")
print(f"Abeilles: {NUM_BEES}")
print(f"Capital: ${account_info.balance:.2f}")
print(f"\nCtrl+C pour arrêter")

input("\nAppuie sur Entrée pour démarrer...")

cycle_count = 0
start_capital = account_info.balance
total_signals = 0

try:
    while True:
        cycle_count += 1
        
        # Capital actuel
        acc = mt5.account_info()
        current_capital = acc.balance if acc else start_capital
        profit = current_capital - start_capital
        
        # Prix actuel
        tick = mt5.symbol_info_tick(SYMBOL)
        price = tick.bid if tick else 0
        
        print(f"\n{'='*70}")
        print(f"CYCLE {cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"💰 ${current_capital:.2f} ({profit:+.2f}) | 📊 {price:.2f}")
        print(f"{'='*70}")
        
        # Appeler run_cycle (qui génère et exécute maintenant)
        try:
            hive.run_cycle()
        except Exception as e:
            print(f"⚠️  Erreur cycle: {e}")
        
        # Attendre
        time.sleep(3)
        
        # Évolution tous les 10 cycles
        if cycle_count % 10 == 0:
            print(f"\n🔄 Évolution cycle {cycle_count}...")
            try:
                hive.evolve()
                print(f"✅ {len(hive.bees)} abeilles actives")
            except Exception as e:
                print(f"⚠️  Erreur évolution: {e}")

except KeyboardInterrupt:
    print("\n\n" + "="*70)
    print("ARRÊT (Ctrl+C)")
    print("="*70)
    
    acc = mt5.account_info()
    final_capital = acc.balance if acc else start_capital
    total_profit = final_capital - start_capital
    
    print(f"\nCycles: {cycle_count}")
    print(f"Capital initial: ${start_capital:.2f}")
    print(f"Capital final: ${final_capital:.2f}")
    print(f"Profit/Perte: ${total_profit:+.2f}")
    
    # Cleanup
    try:
        hive.shutdown()
    except:
        pass
    
    mt5.shutdown()
    print("\n✅ Session terminée")

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    
    try:
        hive.shutdown()
    except:
        pass
    mt5.shutdown()

print("\nAppuie sur Entrée pour quitter...")
input()
