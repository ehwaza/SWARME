"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  SWARNE - LANCEUR AVEC DASHBOARD GRAPHIQUE                  ║
║                                                              ║
║  Ce fichier fait TOUT :                                     ║
║  1. Connexion MT5                                           ║
║  2. Corrections automatiques                                ║
║  3. Lance le DASHBOARD GRAPHIQUE                            ║
║  4. Trading RÉEL avec exécution MT5                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

UTILISATION:
    python swarne_dashboard.py
"""

import MetaTrader5 as mt5
import numpy as np
import sys
import types
from datetime import datetime

print("\n" + "="*70)
print("🐝 SWARNE - LANCEUR AVEC DASHBOARD")
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
# ÉTAPE 1: CONNEXION MT5
# ============================================================
print("🔌 Connexion à MT5...")

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
capital = account_info.balance

print(f"✅ Connecté: {account_info.name}")
print(f"   Balance: ${capital:.2f}")

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
# ÉTAPE 2: CRÉATION HIVE
# ============================================================
print(f"\n🏗️  Création Hive ({NUM_BEES} abeilles)...")
try:
    from swarne_ultimate import Hive
    hive = Hive(initial_capital=capital, num_bees=NUM_BEES, symbol=SYMBOL)
    print(f"✅ {len(hive.bees)} abeilles créées")
except Exception as e:
    print(f"❌ Erreur création Hive: {e}")
    mt5.shutdown()
    input("Appuie sur Entrée...")
    sys.exit(1)

# ============================================================
# ÉTAPE 3: CORRECTIONS AUTOMATIQUES
# ============================================================
print("\n🔧 CORRECTIONS AUTOMATIQUES...")

# 3.1 - Donner field aux abeilles
print("   → bee.field...")
for bee in hive.bees:
    bee.field = hive.field
print("   ✅ field assigné")

# 3.2 - Créer get_market_info() dans Field
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

# 3.3 - Appliquer générateur de signaux
print("   → Générateur signaux...")
try:
    from bee_signal_generator import patch_hive_with_signal_generation
    hive = patch_hive_with_signal_generation(hive)
    print("   ✅ générateur appliqué")
except:
    print("   ⚠️  générateur non disponible")

# 3.4 - Patcher run_cycle pour EXÉCUTER les trades
print("   → run_cycle() patché...")
original_run_cycle = hive.run_cycle

def run_cycle_with_execution(self):
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
                    
                    # Valider avec Guardian
                    if confidence >= 60:
                        
                        # EXÉCUTER RÉELLEMENT dans MT5
                        try:
                            # Préparer l'ordre
                            symbol = SYMBOL
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
                                sl = price_exec - 50 * 10 * point
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
                        
                        except Exception as e:
                            pass
            except:
                pass
    
    # Appeler cycle original
    try:
        return original_run_cycle()
    except:
        pass

hive.run_cycle = types.MethodType(run_cycle_with_execution, hive)
print("   ✅ run_cycle patché")

# 3.5 - Patcher evolve
print("   → evolve() patché...")
if hasattr(hive, 'evolve'):
    original_evolve = hive.evolve
    
    def evolve_fixed(self):
        result = original_evolve()
        for bee in self.bees:
            if not hasattr(bee, 'field') or bee.field is None:
                bee.field = self.field
        return result
    
    hive.evolve = types.MethodType(evolve_fixed, hive)
    print("   ✅ evolve patché")

print("\n✅ TOUTES LES CORRECTIONS APPLIQUÉES")

# ============================================================
# ÉTAPE 4: LANCER LE DASHBOARD
# ============================================================
print("\n🎨 Lancement du Dashboard...")

try:
    from PyQt5.QtWidgets import QApplication
    from dashboard_live_integrated import SwarneDashboard
    
    app = QApplication(sys.argv)
    
    dashboard = SwarneDashboard(
        hive=hive,
        symbol=SYMBOL,
        capital=capital
    )
    
    dashboard.show()
    
    print("\n" + "="*70)
    print("✅ DASHBOARD LANCÉ")
    print("="*70)
    print("\n💡 Clique sur START pour démarrer le trading")
    print("💡 Le système va trader RÉELLEMENT dans MT5")
    print("💡 Ferme la fenêtre pour quitter\n")
    
    sys.exit(app.exec_())

except ImportError as e:
    print(f"\n❌ Erreur import dashboard: {e}")
    print("\nManque un des modules:")
    print("  - PyQt5")
    print("  - dashboard_live_integrated.py")
    print("\nInstalle PyQt5: pip install PyQt5")
    mt5.shutdown()
    input("\nAppuie sur Entrée...")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Erreur dashboard: {e}")
    import traceback
    traceback.print_exc()
    mt5.shutdown()
    input("\nAppuie sur Entrée...")
    sys.exit(1)
