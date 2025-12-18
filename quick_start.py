#!/usr/bin/env python3
"""
🐝 SWARNE! - QUICK START V2.0
Lanceur unifié pour toutes les fonctionnalités SWARNE
"""

import sys
import os
import time
import json
from datetime import datetime

# Import MT5 utilities
try:
    from mt5_utils import (
        normalize_symbol,
        load_mt5_data,
        get_available_symbols,
        mt5_to_pandas_timeframe
    )
    MT5_UTILS_AVAILABLE = True
except ImportError:
    MT5_UTILS_AVAILABLE = False
    print("⚠️  mt5_utils not found, limited functionality")

# ============================================================
# FIX UNICODE POUR WINDOWS
# ============================================================
import io
import logging

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    import locale
    if hasattr(locale, 'getpreferredencoding'):
        locale.getpreferredencoding = lambda: 'UTF-8'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


# ============================================================
# BANNER
# ============================================================
def print_banner():
    """Afficher le banner SWARNE"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    🐝 SWARNE! - THE HIVE 🐝                      ║
║                  Système d'Essaim de Trading                      ║
║                    Quick Start - Version 2.0                      ║
╚══════════════════════════════════════════════════════════════════╝
""")


def print_menu():
    """Afficher le menu principal"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                       🎮 MENU PRINCIPAL 🎮                       ║
╚══════════════════════════════════════════════════════════════════╝

1️⃣  📊 Démo Rapide (V1)           - Test 5 cycles avec l'essaim
2️⃣  🎨 Dashboard Live Trading     - Interface + Trading temps réel ✨
3️⃣  📈 Backtesting                - Tester sur historique
4️⃣  🤖 Entraîner Modèle ML        - LSTM prédiction
5️⃣  🔄 Mode Live Trading          - Trading console temps réel
6️⃣  ⚙️  Configuration              - Modifier les paramètres
7️⃣  📚 Documentation               - Aide et tutoriels
8️⃣  🧪 Tests Système              - Vérifier installation
9️⃣  🚀 MODE PRODUCTION UNIFIÉ      - Coordination + Action + Adaptation 🔥
🔟  🔍 Diagnostic Signaux          - Pourquoi l'essaim ne trade pas ? 🐝
0️⃣  ❌ Quitter

""")


# ============================================================
# VÉRIFICATION DES DÉPENDANCES
# ============================================================
def check_dependencies(full_check=False):
    """Vérifier les dépendances installées"""
    print("🔍 Vérification des dépendances...\n")
    
    dependencies = {
        'core': ['numpy', 'pandas', 'MetaTrader5'],
        'ml': ['tensorflow', 'scikit-learn'],
        'dashboard': ['PyQt5', 'pyqtgraph'],
        'notifications': ['telegram'],
        'advanced': ['ta', 'yaml']
    }
    
    results = {}
    
    # Core (toujours vérifier)
    for dep in dependencies['core']:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
            results[dep] = True
        except ImportError:
            print(f"  ❌ {dep} - MANQUANT")
            results[dep] = False
    
    # Optionnels (si full_check)
    if full_check:
        print("\n📦 Dépendances optionnelles:\n")
        for category, deps in dependencies.items():
            if category == 'core':
                continue
            print(f"\n  {category.upper()}:")
            for dep in deps:
                try:
                    __import__(dep)
                    print(f"    ✅ {dep}")
                    results[dep] = True
                except ImportError:
                    print(f"    ⚠️  {dep} - Non installé (optionnel)")
                    results[dep] = False
    
    # Vérifier MT5
    all_core_ok = all(results.get(dep, False) for dep in dependencies['core'])
    
    if all_core_ok:
        print("\n✅ Toutes les dépendances essentielles sont installées !\n")
    else:
        print("\n❌ Certaines dépendances essentielles manquent.")
        print("   Installez-les avec: pip install -r requirements.txt\n")
    
    return all_core_ok, results


# ============================================================
# TEST CONNEXION MT5
# ============================================================
def test_mt5_connection():
    """Tester la connexion à MetaTrader 5"""
    print("🔌 Test de connexion à MetaTrader 5...\n")
    
    try:
        import MetaTrader5 as mt5
        
        if not mt5.initialize():
            print("  ❌ Impossible de se connecter à MT5")
            print("  💡 Assurez-vous que MetaTrader 5 est ouvert\n")
            return False
        
        account_info = mt5.account_info()
        if account_info is None:
            print("  ❌ Impossible de récupérer les infos du compte\n")
            mt5.shutdown()
            return False
        
        print(f"  ✅ Connecté au compte: {account_info.login}")
        print(f"  💰 Balance: ${account_info.balance:,.2f}")
        print(f"  📊 Server: {account_info.server}\n")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}\n")
        return False


# ============================================================
# CHARGER CONFIGURATION
# ============================================================
def load_config():
    """Charger la configuration"""
    config_files = ['config.json', 'configs/config_v2.yaml']
    
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                if config_file.endswith('.json'):
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                elif config_file.endswith('.yaml'):
                    import yaml
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)
                
                print(f"✅ Configuration chargée: {config_file}")
                return config
            except Exception as e:
                print(f"⚠️  Erreur de chargement: {e}")
    
    print("⚠️  Aucune configuration trouvée, utilisation des valeurs par défaut")
    return {
        'capital': {'initial_capital': 10000.0},
        'swarm': {'num_bees': 20},
        'trading': {'symbols': ['EURUSD']}
    }


# ============================================================
# 1. DÉMO RAPIDE (V1)
# ============================================================
def run_quick_demo():
    """Lancer la démo rapide V1"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    📊 DÉMO RAPIDE - V1.0                         ║
╚══════════════════════════════════════════════════════════════════╝

📝 Cette démo va :
  1. Créer un essaim de 10 abeilles
  2. Exécuter 5 cycles de trading
  3. Afficher les statistiques finales
  
⏱️  Durée estimée: 30 secondes
""")
    
    response = input("Lancer la démonstration ? (o/n): ").strip().lower()
    
    if response != 'o':
        print("⏹️  Démo annulée\n")
        return
    
    print("\n" + "="*60)
    print("🚀 DÉMARRAGE DE LA DÉMONSTRATION")
    print("="*60 + "\n")
    
    try:
        from swarne_ultimate import Hive
        
        # Configuration démo
        capital = 10000.0
        num_bees = 10
        symbol = "EURUSD"
        cycles = 5
        
        print(f"Configuration de démo:")
        print(f"  💰 Capital: ${capital:,.2f}")
        print(f"  🐝 Abeilles: {num_bees}")
        print(f"  📊 Symbole: {symbol}")
        print(f"  🔄 Cycles: {cycles}\n")
        
        # Créer la ruche
        print("🏗️  Création de la ruche...")
        hive = Hive(initial_capital=capital, num_bees=num_bees, symbol=symbol)
        print("✅ Ruche créée avec succès !\n")
        
        # Exécuter les cycles
        print("🔄 Exécution des cycles de trading...\n")
        
        for i in range(cycles):
            print(f"--- Cycle {i+1}/{cycles} ---")
            hive.run_cycle()
            time.sleep(3)
            print()
        
        # Statistiques finales
        print("\n" + "="*60)
        print("📊 STATISTIQUES FINALES")
        print("="*60 + "\n")
        hive.print_statistics()
        
        # Arrêt
        print("\n🛑 Arrêt de la ruche...")
        hive.shutdown()
        
        print("\n✅ Démonstration terminée avec succès !\n")
        
    except Exception as e:
        print(f"\n❌ Erreur pendant la démo: {e}\n")
        logger.exception("Erreur démo")


# ============================================================
# 2. DASHBOARD LIVE INTÉGRÉ (V2)
# ============================================================
def launch_dashboard():
    """Lancer le dashboard PyQt5 avec Live Trading intégré"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              🎨 DASHBOARD LIVE TRADING - V2.0                    ║
╚══════════════════════════════════════════════════════════════════╝

Le dashboard va s'ouvrir avec :
  📊 Métriques temps réel (Capital, Bees, Trades, P&L)
  📈 Graphique d'equity animé
  🐝 État de l'essaim
  🎮 Contrôles START/STOP/REFRESH
  📝 Activity log
  
✨ NOUVEAU : Cliquez START pour lancer le trading en temps réel !
  
⚠️  Nécessite PyQt5 installé
""")
    
    response = input("Lancer le dashboard ? (o/n): ").strip().lower()
    
    if response != 'o':
        print("⏹️  Dashboard annulé\n")
        return
    
    try:
        print("\n🚀 Lancement du dashboard...\n")
        
        # Vérifier PyQt5
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            print("❌ PyQt5 n'est pas installé !")
            print("   Installez avec: pip install PyQt5 pyqtgraph --break-system-packages\n")
            return
        
        # Essayer d'importer le dashboard intégré
        try:
            from dashboard_live_integrated import SwarneDashboard
            print("✅ Dashboard Live Intégré chargé")
        except ImportError:
            # Fallback sur l'ancien dashboard
            try:
                from dashboard_main import SwarneDashboard
                print("⚠️  Dashboard classique chargé (pas de live trading)")
            except ImportError:
                print("❌ Aucun fichier dashboard trouvé !")
                print("   Téléchargez dashboard_live_integrated.py\n")
                return
        
        # Paramètres
        print("\n⚙️  Configuration:")
        symbol = input("  📊 Symbole [EURUSD]: ").strip().upper() or "EURUSD"
        bees_input = input("  🐝 Nombre d'abeilles [20]: ").strip()
        num_bees = int(bees_input) if bees_input else 20
        
        # ====================================
        # CONNEXION MT5 AUTOMATIQUE
        # ====================================
        print(f"\n🔌 Connexion à MT5 pour symbole {symbol}...")
        try:
            from mt5_real_connector import initialize_mt5_system
            connector, real_capital = initialize_mt5_system(symbol)
            
            if connector is None or real_capital is None:
                print("❌ Impossible de se connecter à MT5")
                print("   Mode fallback: capital par défaut\n")
                capital_input = input("  💰 Capital initial [10000]: ").strip()
                capital = float(capital_input) if capital_input else 10000.0
                connector = None
            else:
                capital = real_capital
                print(f"✅ Capital récupéré depuis MT5: ${capital:,.2f}\n")
        except ImportError:
            print("⚠️  mt5_real_connector.py non trouvé")
            print("   Mode fallback: capital par défaut\n")
            capital_input = input("  💰 Capital initial [10000]: ").strip()
            capital = float(capital_input) if capital_input else 10000.0
            connector = None
        # ====================================
        
        # Créer la Hive
        print("\n🏗️  Création de la Hive...")
        from swarne_ultimate import Hive
        hive = Hive(initial_capital=capital, num_bees=num_bees, symbol=symbol)
        print(f"✅ Hive créée: {num_bees} abeilles, ${capital:,.0f}\n")
        
        # ====================================
        # CONNECTEUR MT5: Attacher au Guardian
        # ====================================
        if 'connector' in locals() and connector is not None:
            print("🔌 Attachement du connecteur MT5 au Guardian...")
            try:
                from mt5_real_connector import patch_guardian_with_mt5_connector
                patch_guardian_with_mt5_connector(hive.guardian, connector)
                print(f"✅ Guardian connecté à MT5\n")
            except Exception as e:
                print(f"⚠️  Erreur connexion Guardian: {e}\n")
        # ====================================
        
        # ====================================
        # FIELD ACCESS: Donner accès au Field aux abeilles
        # ====================================
        print("🌸 Attribution du Field aux abeilles...")
        try:
            from patch_field_access import patch_hive_give_field_to_bees
            hive = patch_hive_give_field_to_bees(hive)
            print("✅ Field assigné à toutes les abeilles !\n")
        except ImportError:
            print("⚠️  patch_field_access.py non trouvé")
            print("   Téléchargez patch_field_access.py\n")
            # Fallback: donner field manuellement
            if hasattr(hive, 'field'):
                for bee in hive.bees:
                    if not hasattr(bee, 'field') or bee.field is None:
                        bee.field = hive.field
                print("✅ Field assigné manuellement\n")
        except Exception as e:
            print(f"⚠️  Erreur field patch: {e}\n")
        # ====================================
        
        # ====================================
        # GÉNÉRATEUR DE SIGNAUX: Ajouter generate_signal() aux abeilles
        # ====================================
        print("🐝 Ajout de la génération de signaux aux abeilles...")
        try:
            from bee_signal_generator import patch_hive_with_signal_generation
            hive = patch_hive_with_signal_generation(hive)
            print("✅ Génération de signaux ajoutée !\n")
        except ImportError:
            print("⚠️  bee_signal_generator.py non trouvé")
            print("   Téléchargez bee_signal_generator.py\n")
        except Exception as e:
            print(f"⚠️  Erreur générateur: {e}\n")
        # ====================================
        
        # ====================================
        # PATCH: Activer les abeilles !
        # ====================================
        print("🔧 Application du patch 'Abeilles Actives'...")
        try:
            from patch_active_bees import patch_hive_for_active_trading
            hive = patch_hive_for_active_trading(hive)
            print("✅ Patch appliqué: Génération de signaux activée !\n")
        except ImportError:
            print("⚠️  patch_active_bees.py non trouvé")
            print("   Téléchargez patch_active_bees.py pour activer les abeilles\n")
        except Exception as e:
            print(f"⚠️  Erreur patch: {e}\n")
        # ====================================
        
        # Lancer le dashboard
        app = QApplication(sys.argv)
        dashboard = SwarneDashboard(hive=hive, symbol=symbol, capital=capital)
        dashboard.show()
        
        print("✅ Dashboard lancé !")
        print("💡 Cliquez sur START pour démarrer le trading")
        print("💡 Fermez la fenêtre pour revenir au menu\n")
        
        sys.exit(app.exec_())
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Dashboard fermé\n")
    except Exception as e:
        print(f"\n❌ Erreur: {e}\n")
        logger.exception("Erreur dashboard")


# ============================================================
# 3. BACKTESTING
# ============================================================
def run_backtest():
    """Lancer un backtest"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                      📈 BACKTESTING ENGINE                       ║
╚══════════════════════════════════════════════════════════════════╝

Testez votre stratégie sur des données historiques.
""")
    
    # Paramètres
    print("\n📅 Période de backtest:")
    start_date = input("  Date de début (YYYY-MM-DD) [2023-01-01]: ").strip() or "2023-01-01"
    end_date = input("  Date de fin (YYYY-MM-DD) [2024-12-16]: ").strip() or "2024-12-16"
    
    print("\n📊 Symboles:")
    symbols_input = input("  Symboles (séparés par virgule) [EURUSD]: ").strip() or "EURUSD"
    
    # Normaliser les symboles
    if MT5_UTILS_AVAILABLE:
        symbols = [normalize_symbol(s.strip()) for s in symbols_input.split(',')]
    else:
        symbols = [s.strip().upper() for s in symbols_input.split(',')]
    
    print("\n💰 Capital:")
    capital = float(input("  Capital initial [10000]: ").strip() or "10000")
    
    print("\n🐝 Configuration:")
    num_bees = int(input("  Nombre d'abeilles [20]: ").strip() or "20")
    
    print(f"""
Configuration du backtest:
  📅 Période: {start_date} → {end_date}
  📊 Symboles: {', '.join(symbols)}
  💰 Capital: ${capital:,.2f}
  🐝 Abeilles: {num_bees}
""")
    
    response = input("Lancer le backtest ? (o/n): ").strip().lower()
    
    if response != 'o':
        print("⏹️  Backtest annulé\n")
        return
    
    try:
        print("\n🚀 Lancement du backtest...\n")
        
        from backtesting_engine import BacktestEngine, BacktestConfig
        from swarne_ultimate import Hive
        
        # Configuration
        config = BacktestConfig(
            start_date=start_date,
            end_date=end_date,
            symbols=symbols,
            initial_capital=capital
        )
        
        # Créer la Hive
        hive = Hive(initial_capital=capital, num_bees=num_bees, symbol=symbols[0])
        
        # Créer l'engine
        engine = BacktestEngine(config)
        
        # Lancer
        print("⏳ Backtest en cours... (cela peut prendre quelques minutes)\n")
        results = engine.run(hive)
        
        # Afficher résultats
        print("\n" + "="*60)
        print("📊 RÉSULTATS DU BACKTEST")
        print("="*60 + "\n")
        
        print(f"📈 Performance:")
        print(f"   Total Return: {results.total_pnl_pct:+.2f}%")
        print(f"   Total Trades: {results.total_trades}")
        print(f"   Win Rate: {results.win_rate:.1f}%")
        print(f"   Profit Factor: {results.profit_factor:.2f}\n")
        
        print(f"💰 Capital:")
        print(f"   Initial: ${results.initial_capital:,.2f}")
        print(f"   Final: ${results.final_capital:,.2f}")
        print(f"   Max: ${results.max_capital:,.2f}\n")
        
        print(f"📉 Risk Metrics:")
        print(f"   Max Drawdown: {results.max_drawdown_pct:.2f}%")
        print(f"   Sharpe Ratio: {results.sharpe_ratio:.2f}")
        print(f"   Sortino Ratio: {results.sortino_ratio:.2f}")
        print(f"   Calmar Ratio: {results.calmar_ratio:.2f}\n")
        
        print("✅ Backtest terminé !\n")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}\n")
        logger.exception("Erreur backtest")


# ============================================================
# 4. ENTRAÎNER MODÈLE ML
# ============================================================
def train_ml_model():
    """Entraîner un modèle ML"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                   🤖 ENTRAÎNEMENT MODÈLE ML                      ║
╚══════════════════════════════════════════════════════════════════╝

Entraînez un réseau LSTM pour prédire la direction du marché.
⚠️  Nécessite TensorFlow installé
""")
    
    # Paramètres
    symbol = input("\n📊 Symbole [EURUSD]: ").strip() or "EURUSD"
    
    # Normaliser le symbole
    if MT5_UTILS_AVAILABLE:
        symbol = normalize_symbol(symbol)
    else:
        symbol = symbol.upper()
    
    epochs = int(input("🔄 Nombre d'epochs [50]: ").strip() or "50")
    
    response = input(f"\nEntraîner le modèle sur {symbol} ? (o/n): ").strip().lower()
    
    if response != 'o':
        print("⏹️  Entraînement annulé\n")
        return
    
    try:
        print("\n🚀 Lancement de l'entraînement...\n")
        
        from lstm_predictor import LSTMPredictor, LSTMConfig
        import MetaTrader5 as mt5
        import pandas as pd
        
        # Vérifier TensorFlow
        try:
            import tensorflow as tf
            print(f"✅ TensorFlow {tf.__version__} détecté\n")
        except ImportError:
            print("❌ TensorFlow n'est pas installé !")
            print("   Installez avec: pip install tensorflow\n")
            return
        
        # Charger données historiques
        print(f"📥 Chargement des données historiques pour {symbol}...")
        
        df = None
        
        # Méthode 1: Utiliser mt5_utils si disponible
        if MT5_UTILS_AVAILABLE:
            try:
                df = load_mt5_data(symbol, 'H1', num_bars=10000)
            except Exception as e:
                print(f"⚠️  Erreur avec mt5_utils: {e}")
                df = None
        
        # Méthode 2: Fallback direct MT5
        if df is None or len(df) == 0:
            print("⚠️  Tentative de chargement direct depuis MT5...")
            
            try:
                import MetaTrader5 as mt5
                
                # Initialiser MT5
                if not mt5.initialize():
                    print("❌ MT5 n'est pas ouvert ou ne répond pas\n")
                    print("💡 Solution:")
                    print("   1. Ouvrez MetaTrader 5")
                    print("   2. Connectez-vous à un compte (même DEMO)")
                    print("   3. Relancez l'entraînement\n")
                    return
                
                # Vérifier le symbole
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info is None:
                    print(f"❌ Symbole {symbol} introuvable dans MT5\n")
                    print("💡 Symboles courants: EURUSD, GBPUSD, USDJPY, XAUUSD")
                    print(f"   Vérifiez l'orthographe de: {symbol}\n")
                    mt5.shutdown()
                    return
                
                # Sélectionner le symbole (important !)
                if not mt5.symbol_select(symbol, True):
                    print(f"⚠️  Impossible de sélectionner {symbol}")
                
                # Charger les données
                print(f"📊 Récupération de 10,000 barres H1 pour {symbol}...")
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 10000)
                
                if rates is None or len(rates) == 0:
                    error_code = mt5.last_error()
                    print(f"❌ Erreur MT5: {error_code}")
                    print("💡 Essayez:")
                    print(f"   1. Ouvrir le graphique {symbol} dans MT5")
                    print("   2. Attendre le chargement de l'historique")
                    print("   3. Relancer l'entraînement\n")
                    mt5.shutdown()
                    return
                
                mt5.shutdown()
                
                # Convertir en DataFrame
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                
                # Renommer tick_volume en volume (standard MT5)
                if 'tick_volume' in df.columns and 'volume' not in df.columns:
                    df['volume'] = df['tick_volume']
                
            except Exception as e:
                print(f"❌ Erreur lors du chargement: {e}\n")
                logger.exception("Erreur chargement ML")
                return
        
        # Vérifier qu'on a bien des données
        if df is None or len(df) == 0:
            print("❌ Aucune donnée chargée\n")
            return
        
        print(f"✅ {len(df)} barres chargées pour {symbol}\n")
        
        # Configuration
        config = LSTMConfig(
            sequence_length=60,
            lstm_units=[128, 64, 32],
            epochs=epochs,
            batch_size=32
        )
        
        # Créer et entraîner
        print("🧠 Création du modèle LSTM...\n")
        predictor = LSTMPredictor(config)
        
        print(f"🔄 Entraînement en cours ({epochs} epochs)...")
        print("   Cela peut prendre 10-30 minutes selon votre machine\n")
        
        results = predictor.train(df)
        
        # Résultats
        print("\n" + "="*60)
        print("📊 RÉSULTATS DE L'ENTRAÎNEMENT")
        print("="*60 + "\n")
        
        print(f"✅ Entraînement terminé !")
        print(f"   Loss: {results['loss']:.4f}")
        print(f"   Accuracy: {results['accuracy']:.2%}")
        print(f"   Val Loss: {results['val_loss']:.4f}")
        print(f"   Val Accuracy: {results['val_accuracy']:.2%}\n")
        
        # Sauvegarder
        model_path = f"data/models/lstm_{symbol.lower()}.h5"
        os.makedirs("data/models", exist_ok=True)
        predictor.save_model(model_path)
        
        print(f"💾 Modèle sauvegardé: {model_path}\n")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}\n")
        logger.exception("Erreur ML training")


# ============================================================
# 5. MODE LIVE TRADING
# ============================================================
def run_live_trading():
    """Lancer le trading en temps réel"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                   🔄 MODE LIVE TRADING                           ║
╚══════════════════════════════════════════════════════════════════╝

⚠️  ATTENTION: Mode de trading en temps réel !

Recommandations:
  ✅ Testez d'abord en compte DEMO
  ✅ Commencez avec un petit capital
  ✅ Surveillez régulièrement
  ✅ Ayez un plan d'urgence
""")
    
    # Configuration
    print("\n⚙️  Configuration:")
    capital = float(input("  Capital initial [$10000]: ").strip() or "10000")
    num_bees = int(input("  Nombre d'abeilles [20]: ").strip() or "20")
    symbol = input("  Symbole [EURUSD]: ").strip() or "EURUSD"
    
    # Normaliser le symbole
    if MT5_UTILS_AVAILABLE:
        symbol = normalize_symbol(symbol)
    else:
        symbol = symbol.upper()
    
    print(f"\n💡 Le système va trader avec:")
    print(f"   💰 Capital: ${capital:,.2f}")
    print(f"   🐝 Abeilles: {num_bees}")
    print(f"   📊 Symbole: {symbol}")
    print(f"\n⚠️  Assurez-vous d'être en compte DEMO pour les tests !\n")
    
    response = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ").strip().lower()
    
    if response != 'oui':
        print("⏹️  Mode live annulé\n")
        return
    
    try:
        print("\n🚀 Démarrage du trading en temps réel...\n")
        
        from swarne_ultimate import Hive
        
        # Créer la Hive
        hive = Hive(initial_capital=capital, num_bees=num_bees, symbol=symbol)
        
        print("✅ Hive initialisée")
        print("🔄 Trading en cours... (Ctrl+C pour arrêter)\n")
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                print(f"--- Cycle {cycle_count} ---")
                
                hive.run_cycle()
                
                # Statistiques toutes les 10 cycles
                if cycle_count % 10 == 0:
                    print("\n📊 Statistiques:")
                    hive.print_statistics()
                    print()
                
                # Attendre 60 secondes
                time.sleep(60)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Arrêt demandé par l'utilisateur")
        
        # Arrêt propre
        print("\n🛑 Arrêt de la ruche...")
        hive.print_statistics()
        hive.shutdown()
        
        print("\n✅ Trading arrêté avec succès\n")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}\n")
        logger.exception("Erreur live trading")


# ============================================================
# 6. CONFIGURATION
# ============================================================
def show_configuration():
    """Afficher/Modifier la configuration"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                       ⚙️  CONFIGURATION                          ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    config = load_config()
    
    print("\n📄 Configuration actuelle:\n")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    print("\n💡 Pour modifier la configuration, éditez:")
    print("   - config.json (V1)")
    print("   - configs/config_v2.yaml (V2)\n")
    
    input("Appuyez sur Entrée pour continuer...")


# ============================================================
# 7. DOCUMENTATION
# ============================================================
def show_documentation():
    """Afficher la documentation"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                     📚 DOCUMENTATION                             ║
╚══════════════════════════════════════════════════════════════════╝

📖 Documents disponibles:
  1. README.md          - Documentation V1
  2. README_V2.md       - Documentation V2 complète
  3. MANIFEST.md        - Philosophie du projet
  4. SPRINT_24H_REPORT.md - Rapport de développement

🌐 Ressources en ligne:
  - GitHub: https://github.com/swarne/swarne
  - Discord: https://discord.gg/swarne
  - Twitter: @SwarneAI

💡 Commandes rapides:
  python quick_start.py     - Ce menu
  python run_dashboard.py   - Dashboard uniquement
  python run_backtest.py    - Backtest uniquement

⚠️  Important:
  - Testez TOUJOURS en compte DEMO d'abord
  - Commencez avec un petit capital
  - Surveillez régulièrement le système
  - Le trading comporte des risques
""")
    
    input("\nAppuyez sur Entrée pour continuer...")


# ============================================================
# 9. MODE PRODUCTION UNIFIÉ 🚀
# ============================================================
def run_unified_production_mode():
    """
    Mode Production Unifié
    Coordination + Action + Production + Adaptation
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║            🚀 MODE PRODUCTION UNIFIÉ - SWARNE V2.0 🚀            ║
╚══════════════════════════════════════════════════════════════════╝

🎯 Ce mode active le système complet:

  📡 Phase 1: COORDINATION
     → Synchronisation de l'essaim
     → Établissement de communication
     → Distribution des rôles
     → Calcul du niveau de coordination

  📈 Phase 2: ACTION  
     → Connexion au marché
     → Chargement des prédictions ML
     → Activation du trading coordonné
     → Intensité d'action optimale

  🏭 Phase 3: PRODUCTION
     → Calcul du taux de production
     → Ajustement des paramètres
     → Monitoring continu
     → Optimisation des profits

  🧬 Phase 4: ADAPTATION
     → Ajustement dynamique
     → Apprentissage continu
     → Réaction aux changements
     → Amélioration performance

⚠️  Mode avancé - Recommandé pour utilisateurs expérimentés
⚠️  Testez d'abord en compte DEMO
""")
    
    # ====================================
    # CONNEXION MT5 AUTOMATIQUE
    # ====================================
    print("\n🔌 CONNEXION AUTOMATIQUE À MT5...")
    
    # Importer le connecteur
    try:
        from mt5_real_connector import initialize_mt5_system
    except ImportError:
        print("❌ mt5_real_connector.py non trouvé !")
        print("   Téléchargez mt5_real_connector.py")
        print("   Ou le système utilisera un capital par défaut\n")
        
        # Fallback : demander le capital
        print("\n⚙️  Configuration (mode fallback):")
        symbol = input("  📊 Symbole [EURUSD]: ").strip().upper() or "EURUSD"
        capital_input = input("  💰 Capital initial [10000]: ").strip()
        capital = float(capital_input) if capital_input else 10000.0
        bees_input = input("  🐝 Nombre d'abeilles [20]: ").strip()
        num_bees = int(bees_input) if bees_input else 20
        connector = None
    else:
        # Configuration simplifiée
        print("\n⚙️  Configuration:")
        symbol = input("  📊 Symbole [EURUSD]: ").strip().upper() or "EURUSD"
        bees_input = input("  🐝 Nombre d'abeilles [20]: ").strip()
        num_bees = int(bees_input) if bees_input else 20
        
        # Connexion à MT5 et récupération du capital RÉEL
        print(f"\n🔌 Connexion à MT5 pour symbole {symbol}...")
        connector, real_capital = initialize_mt5_system(symbol)
        
        if connector is None or real_capital is None:
            print("❌ Impossible de se connecter à MT5")
            print("   Vérifiez que MetaTrader 5 est ouvert")
            print("   Le système utilisera un capital par défaut\n")
            
            # Fallback
            capital_input = input("  💰 Capital initial [10000]: ").strip()
            capital = float(capital_input) if capital_input else 10000.0
            connector = None
        else:
            # Capital récupéré de MT5 !
            capital = real_capital
            print(f"\n✅ Capital récupéré depuis MT5: ${capital:,.2f}")
            print(f"   (Vous n'avez pas besoin de le saisir !)\n")
    # ====================================
    
    # Confirmation
    print(f"""
📋 Récapitulatif:
   Symbole: {symbol}
   Capital: ${capital:,.2f}
   Abeilles: {num_bees}
   Mode: PRODUCTION UNIFIÉ

⚠️  Ce mode va :
   1. Créer une Hive coordonnée
   2. Lancer le Dashboard Live
   3. Activer la coordination avancée
   4. Démarrer le trading automatiquement
   5. Adapter en temps réel

⚠️  Assurez-vous d'être en compte DEMO !
""")
    
    response = input("Êtes-vous sûr de continuer ? (oui/non): ").strip().lower()
    
    if response != 'oui':
        print("\n⏹️  Mode production annulé\n")
        return
    
    try:
        print("\n" + "="*60)
        print("🚀 DÉMARRAGE MODE PRODUCTION UNIFIÉ")
        print("="*60 + "\n")
        
        # 1. Créer la Hive
        print("🏗️  Phase 1: Création de la Hive...")
        from swarne_ultimate import Hive
        hive = Hive(initial_capital=capital, num_bees=num_bees, symbol=symbol)
        print(f"✅ Hive créée: {num_bees} abeilles, ${capital:,.0f}\n")
        
        # ====================================
        # CONNECTEUR MT5: Attacher au Guardian
        # ====================================
        if 'connector' in locals() and connector is not None:
            print("🔌 Attachement du connecteur MT5 au Guardian...")
            try:
                from mt5_real_connector import patch_guardian_with_mt5_connector
                patch_guardian_with_mt5_connector(hive.guardian, connector)
                print(f"✅ Guardian connecté à MT5 (Capital: ${capital:,.2f})\n")
            except Exception as e:
                print(f"⚠️  Erreur connexion Guardian: {e}\n")
        # ====================================
        
        # ====================================
        # FIELD ACCESS: Donner accès au Field aux abeilles
        # ====================================
        print("🌸 Attribution du Field aux abeilles...")
        try:
            from patch_field_access import patch_hive_give_field_to_bees
            hive = patch_hive_give_field_to_bees(hive)
            print("✅ Field assigné à toutes les abeilles !\n")
        except ImportError:
            print("⚠️  patch_field_access.py non trouvé")
            print("   Téléchargez patch_field_access.py\n")
            # Fallback: donner field manuellement
            if hasattr(hive, 'field'):
                for bee in hive.bees:
                    if not hasattr(bee, 'field') or bee.field is None:
                        bee.field = hive.field
                print("✅ Field assigné manuellement\n")
        except Exception as e:
            print(f"⚠️  Erreur field patch: {e}\n")
        # ====================================
        
        # ====================================
        # GÉNÉRATEUR DE SIGNAUX: Ajouter generate_signal() aux abeilles
        # ====================================
        print("🐝 Ajout de la génération de signaux aux abeilles...")
        try:
            from bee_signal_generator import patch_hive_with_signal_generation
            hive = patch_hive_with_signal_generation(hive)
            print("✅ Génération de signaux ajoutée !\n")
        except ImportError:
            print("⚠️  bee_signal_generator.py non trouvé")
            print("   Téléchargez bee_signal_generator.py\n")
        except Exception as e:
            print(f"⚠️  Erreur générateur: {e}\n")
        # ====================================
        
        # ====================================
        # PATCH: Activer les abeilles !
        # ====================================
        print("🔧 Application du patch 'Abeilles Actives'...")
        try:
            from patch_active_bees import patch_hive_for_active_trading
            hive = patch_hive_for_active_trading(hive)
            print("✅ Patch appliqué: Génération de signaux activée !\n")
        except ImportError:
            print("⚠️  patch_active_bees.py non trouvé")
            print("   Téléchargez patch_active_bees.py\n")
        except Exception as e:
            print(f"⚠️  Erreur patch: {e}\n")
        # ====================================
        
        # 2. Initialiser le coordinateur
        print("🎯 Phase 2: Initialisation du coordinateur...")
        try:
            from swarm_coordinator import SwarmCoordinator
            coordinator = SwarmCoordinator(hive)
            print("✅ Coordinateur initialisé\n")
        except ImportError:
            print("⚠️  swarm_coordinator.py non trouvé")
            print("   Téléchargez swarm_coordinator.py")
            print("   Mode production désactivé, mode standard activé\n")
            coordinator = None
        
        # 3. Démarrer la coordination
        if coordinator:
            print("📡 Phase 3: Démarrage de la coordination...")
            coordinator.start_production_mode()
            print()
        
        # 4. Lancer le Dashboard avec le coordinateur
        print("🎨 Phase 4: Lancement du Dashboard intégré...")
        
        try:
            from PyQt5.QtWidgets import QApplication
            from dashboard_live_integrated import SwarneDashboard
            
            app = QApplication(sys.argv)
            dashboard = SwarneDashboard(
                hive=hive, 
                symbol=symbol, 
                capital=capital
            )
            
            # Attacher le coordinateur au dashboard si disponible
            if coordinator:
                dashboard.coordinator = coordinator
                print("✅ Coordinateur attaché au dashboard")
            
            dashboard.show()
            
            print("\n" + "="*60)
            print("✅ MODE PRODUCTION UNIFIÉ ACTIVÉ")
            print("="*60 + "\n")
            
            print("📊 Dashboard lancé avec coordination avancée !")
            print("💡 Cliquez sur START pour démarrer le trading coordonné")
            print("💡 Le système s'adaptera automatiquement")
            print("💡 Fermez la fenêtre pour revenir au menu\n")
            
            if coordinator:
                # Afficher le status
                status = coordinator.get_status()
                print("📈 Status de coordination:")
                print(f"   Mode: {status['mode']}")
                print(f"   Coordination: {status['coordination_level']:.1%}")
                print(f"   Action Intensity: {status['action_intensity']:.1%}")
                print(f"   Production Rate: {status['production_rate']:.2f} trades/h")
                print(f"   Adaptation Score: {status['adaptation_score']:.1%}\n")
            
            # Lancer l'application
            sys.exit(app.exec_())
            
        except ImportError as e:
            print(f"❌ Erreur dashboard: {e}")
            print("   Installez: pip install PyQt5 pyqtgraph --break-system-packages\n")
            
            # Fallback: mode console avec coordinateur
            if coordinator:
                print("\n📟 Fallback: Mode console avec coordination")
                run_console_with_coordinator(hive, coordinator)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt demandé")
        if 'coordinator' in locals() and coordinator:
            coordinator.shutdown()
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}\n")
        logger.exception("Erreur mode production")


def run_console_with_coordinator(hive, coordinator):
    """Exécuter le trading en mode console avec coordinateur"""
    print("\n🎮 Trading coordonné en mode console")
    print("   Appuyez sur Ctrl+C pour arrêter\n")
    
    try:
        cycle = 0
        
        while True:
            cycle += 1
            
            # Exécuter un cycle
            hive.run_cycle()
            
            # Adapter si nécessaire (tous les 10 cycles)
            if cycle % 10 == 0:
                coordinator.adapt_to_performance()
                
                # Afficher status
                status = coordinator.get_status()
                print(f"\n📊 Status (Cycle {cycle}):")
                print(f"   Capital: ${hive.guardian.capital:,.2f}")
                print(f"   Coordination: {status['coordination_level']:.1%}")
                print(f"   Action Intensity: {status['action_intensity']:.1%}")
                print(f"   Adaptation Score: {status['adaptation_score']:.1%}\n")
            
            # Pause
            time.sleep(4)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt demandé")
    
    finally:
        coordinator.shutdown()
        hive.shutdown()
        print("\n✅ Trading arrêté avec succès\n")


# ============================================================
# 8. TESTS SYSTÈME
# ============================================================
def run_system_tests():
    """Exécuter les tests système"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                      🧪 TESTS SYSTÈME                            ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    print("\n1️⃣  Test des dépendances...")
    deps_ok, results = check_dependencies(full_check=True)
    
    print("\n2️⃣  Test de connexion MT5...")
    mt5_ok = test_mt5_connection()
    
    print("\n3️⃣  Test de configuration...")
    config = load_config()
    config_ok = config is not None
    print(f"  {'✅' if config_ok else '❌'} Configuration chargée\n")
    
    # Résumé
    print("="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60 + "\n")
    
    print(f"  Dépendances core: {'✅' if deps_ok else '❌'}")
    print(f"  Connexion MT5: {'✅' if mt5_ok else '❌'}")
    print(f"  Configuration: {'✅' if config_ok else '❌'}\n")
    
    if deps_ok and mt5_ok and config_ok:
        print("✅ Tous les tests sont passés ! Système prêt.\n")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez l'installation.\n")
    
    input("Appuyez sur Entrée pour continuer...")


# ============================================================
# 10. DIAGNOSTIC GÉNÉRATION DE SIGNAUX
# ============================================================
def run_diagnostic():
    """Lancer le diagnostic de génération de signaux"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              🔍 DIAGNOSTIC GÉNÉRATION DE SIGNAUX 🔍              ║
╚══════════════════════════════════════════════════════════════════╝

Ce diagnostic va :
  ✅ Tester la génération de signaux des abeilles
  ✅ Identifier pourquoi l'essaim ne trade pas
  ✅ Afficher le code de generate_signal()
  ✅ Tester la validation du Guardian
  
⏱️  Durée: ~30 secondes
""")
    
    response = input("Lancer le diagnostic ? (o/n): ").strip().lower()
    
    if response != 'o':
        print("⏹️  Diagnostic annulé\n")
        return
    
    try:
        # Importer et lancer le diagnostic
        print("\n🚀 Lancement du diagnostic...\n")
        
        try:
            from diagnostic_signaux import main as run_diagnostic_main
            run_diagnostic_main()
        except ImportError:
            print("❌ diagnostic_signaux.py non trouvé !")
            print("   Téléchargez diagnostic_signaux.py")
            print("   Placez-le dans le même dossier que quick_start.py\n")
            
            # Alternative : essayer de le créer à la volée
            print("💡 Voulez-vous que je crée le fichier maintenant ? (o/n): ")
            create = input().strip().lower()
            
            if create == 'o':
                print("   Création de diagnostic_signaux.py...")
                # On pourrait créer le fichier ici si nécessaire
                print("   ⚠️  Pour l'instant, téléchargez-le manuellement\n")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Diagnostic interrompu\n")
    except Exception as e:
        print(f"\n❌ Erreur: {e}\n")
        logger.exception("Erreur diagnostic")


# ============================================================
# MAIN MENU
# ============================================================
def main():
    """Fonction principale avec menu"""
    
    print_banner()
    
    # Vérifications initiales rapides
    print("🔍 Vérifications initiales...\n")
    deps_ok, _ = check_dependencies(full_check=False)
    
    if not deps_ok:
        print("⚠️  Installation incomplète. Lancez le test système (option 8) pour plus de détails.\n")
    
    # Menu principal
    while True:
        print_menu()
        
        choice = input("Votre choix (0-10): ").strip()
        
        print()
        
        if choice == '1':
            run_quick_demo()
        elif choice == '2':
            launch_dashboard()
        elif choice == '3':
            run_backtest()
        elif choice == '4':
            train_ml_model()
        elif choice == '5':
            run_live_trading()
        elif choice == '6':
            show_configuration()
        elif choice == '7':
            show_documentation()
        elif choice == '8':
            run_system_tests()
        elif choice == '9':
            run_unified_production_mode()
        elif choice == '10' or choice.lower() == 'd':
            run_diagnostic()
        elif choice == '0':
            print("""
╔══════════════════════════════════════════════════════════════════╗
║                    🐝 SWARNE! - MERCI ! 🐝                       ║
║                                                                  ║
║  "L'union fait la force" - Intelligence collective              ║
║                                                                  ║
║  🚀 Bon trading avec SWARNE! 🚀                                 ║
╚══════════════════════════════════════════════════════════════════╝
""")
            sys.exit(0)
        else:
            print("❌ Choix invalide. Choisissez entre 0 et 10 (ou tapez 'd' pour diagnostic).\n")
        
        input("Appuyez sur Entrée pour revenir au menu...")
        print("\n" * 2)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Programme interrompu par l'utilisateur\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}\n")
        logger.exception("Erreur fatale")
        sys.exit(1)
