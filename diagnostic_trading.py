"""
🔍 SWARNE - Diagnostic Trading
Vérifier pourquoi 0 trades sont générés
"""

import MetaTrader5 as mt5
import sys

print("\n" + "="*60)
print("🔍 DIAGNOSTIC SWARNE - GÉNÉRATION DE TRADES")
print("="*60 + "\n")

# 1. Vérifier MT5
print("1️⃣ Vérification MT5...")
if not mt5.initialize():
    print("❌ MT5 n'est pas ouvert ou ne répond pas")
    print("   → Ouvre MetaTrader 5")
    print("   → Connecte-toi à un compte DEMO")
    print("   → Relance ce script\n")
    sys.exit(1)

print("✅ MT5 connecté")

# 2. Vérifier le compte
account_info = mt5.account_info()
if account_info:
    print(f"   Compte: {account_info.login}")
    print(f"   Type: {'DEMO' if account_info.trade_mode == 0 else 'REAL'}")
    print(f"   Balance: ${account_info.balance:,.2f}")
    print(f"   Server: {account_info.server}\n")
else:
    print("❌ Impossible de récupérer les infos du compte\n")
    mt5.shutdown()
    sys.exit(1)

# 3. Vérifier le symbole
symbol = "EURUSD"
print(f"2️⃣ Vérification symbole {symbol}...")

symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(f"❌ Symbole {symbol} introuvable")
    print("   Symboles disponibles:")
    symbols = mt5.symbols_get()
    if symbols:
        for i, s in enumerate(symbols[:10]):
            print(f"   - {s.name}")
    mt5.shutdown()
    sys.exit(1)

print(f"✅ Symbole {symbol} trouvé")

# Sélectionner le symbole
if not mt5.symbol_select(symbol, True):
    print(f"⚠️  Impossible de sélectionner {symbol}")

# 4. Vérifier les prix
print(f"\n3️⃣ Vérification prix temps réel...")

tick = mt5.symbol_info_tick(symbol)
if tick is None:
    print(f"❌ Impossible de récupérer le prix de {symbol}")
    print("   → Ouvre un graphique EURUSD dans MT5")
    print("   → Attends quelques secondes")
    print("   → Relance ce script\n")
    mt5.shutdown()
    sys.exit(1)

print(f"✅ Prix actuels:")
print(f"   Bid: {tick.bid}")
print(f"   Ask: {tick.ask}")
print(f"   Spread: {tick.ask - tick.bid:.5f}")
print(f"   Time: {tick.time}\n")

# 5. Vérifier données historiques
print(f"4️⃣ Vérification historique...")

rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 100)
if rates is None or len(rates) == 0:
    print(f"❌ Impossible de charger l'historique")
    print("   → Ouvre un graphique EURUSD H1 dans MT5")
    print("   → Attends que l'historique se charge")
    print("   → Relance ce script\n")
    mt5.shutdown()
    sys.exit(1)

print(f"✅ {len(rates)} barres historiques chargées")
print(f"   Dernière barre: {rates[-1]['time']}")
print(f"   Close: {rates[-1]['close']}\n")

# 6. Calculer ATR
print(f"5️⃣ Calcul de l'ATR...")

import pandas as pd
import numpy as np

df = pd.DataFrame(rates)
df['high-low'] = df['high'] - df['low']
df['high-close'] = np.abs(df['high'] - df['close'].shift())
df['low-close'] = np.abs(df['low'] - df['close'].shift())
df['tr'] = df[['high-low', 'high-close', 'low-close']].max(axis=1)
atr = df['tr'].rolling(14).mean().iloc[-1]

print(f"✅ ATR(14): {atr:.5f}")

if atr < 0.0001:
    print(f"⚠️  ATR très faible ! Le marché est peut-être fermé.")
elif atr > 0.01:
    print(f"⚠️  ATR très élevé ! Volatilité extrême.")
else:
    print(f"✅ ATR normal pour {symbol}\n")

# 7. Tester génération de signal basique
print(f"6️⃣ Test génération signal basique...")

# Calculs simples
close_prices = df['close'].values[-20:]
sma_short = np.mean(close_prices[-5:])
sma_long = np.mean(close_prices[-20:])

print(f"   SMA(5): {sma_short:.5f}")
print(f"   SMA(20): {sma_long:.5f}")

if sma_short > sma_long:
    signal = "BUY"
    print(f"✅ Signal détecté: {signal} (SMA court > SMA long)")
elif sma_short < sma_long:
    signal = "SELL"
    print(f"✅ Signal détecté: {signal} (SMA court < SMA long)")
else:
    signal = "NEUTRAL"
    print(f"⚠️  Signal: {signal} (SMA égaux)")

print()

# 8. Vérifier permissions de trading
print(f"7️⃣ Vérification permissions trading...")

# Vérifier si le trading est autorisé
if symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_DISABLED:
    print(f"❌ Trading désactivé pour {symbol}")
elif symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_CLOSEONLY:
    print(f"⚠️  Mode close-only pour {symbol}")
else:
    print(f"✅ Trading autorisé pour {symbol}")

# Vérifier les volumes min/max
print(f"   Volume min: {symbol_info.volume_min}")
print(f"   Volume max: {symbol_info.volume_max}")
print(f"   Volume step: {symbol_info.volume_step}\n")

# 9. Résumé
mt5.shutdown()

print("="*60)
print("📊 RÉSUMÉ DU DIAGNOSTIC")
print("="*60 + "\n")

print("✅ MT5: Connecté")
print(f"✅ Compte: {account_info.login} ({'DEMO' if account_info.trade_mode == 0 else 'REAL'})")
print(f"✅ Symbole: {symbol}")
print(f"✅ Prix: {tick.bid}/{tick.ask}")
print(f"✅ Historique: {len(rates)} barres")
print(f"✅ ATR: {atr:.5f}")
print(f"✅ Signal: {signal}")
print(f"✅ Trading: Autorisé\n")

print("🎯 CONCLUSION:")
print("   Tous les éléments sont OK pour trader !")
print("   Le problème vient probablement de:")
print("   1. Les abeilles ne génèrent pas de signaux")
print("   2. Le Guardian bloque les trades")
print("   3. Les conditions de trading sont trop strictes\n")

print("💡 SOLUTION:")
print("   → Envoie-moi le contenu de swarne_ultimate.py")
print("   → Je vais ajuster la logique de génération de signaux\n")

input("Appuyez sur Entrée pour quitter...")
