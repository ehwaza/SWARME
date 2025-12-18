# 🐝⚡ SWARNE V2.0 - DOCUMENTATION COMPLÈTE ⚡🐝

```
╔══════════════════════════════════════════════════════════════╗
║     🚀 SYSTÈME D'ESSAIM DE TRADING ULTRA-AVANCÉ 🚀          ║
║     6 SYSTÈMES INTÉGRÉS - SPRINT DE DÉV 24H                 ║
╚══════════════════════════════════════════════════════════════╝
```

## 🎯 **NOUVEAUTÉS V2.0**

### ✅ **1. GÉNÉTIQUE AVANCÉE**
- Sélection par tournoi, roulette, rang
- Crossover multi-points, blend, arithmétique
- Mutation adaptative, gaussienne, polynomiale
- Immigration automatique pour diversité
- Élitisme dynamique

### ✅ **2. BACKTESTING COMPLET**
- Moteur vectorisé haute performance
- Métriques avancées (Sharpe, Sortino, Calmar)
- Walk-forward analysis
- Support multi-symboles
- Rapports HTML interactifs

### ✅ **3. MACHINE LEARNING (LSTM)**
- Prédiction de direction du marché
- Architecture LSTM multi-couches
- Feature engineering automatique
- Ensemble de modèles
- Sauvegarde/chargement modèles

### ✅ **4. MULTI-SYMBOLES**
- Trading simultané sur plusieurs paires
- Analyse de corrélation en temps réel
- Optimisation de portefeuille
- Gestion d'exposition
- Réduction de risque par diversification

### ✅ **5. DASHBOARD PyQt5**
- Interface graphique temps réel
- Graphiques d'equity interactifs
- Visualisation de l'essaim
- Panel de contrôle
- Logs en direct

### ✅ **6. NOTIFICATIONS**
- Telegram (signaux + rapports)
- Email (à implémenter)
- Alertes configurables

---

## 📦 **ARCHITECTURE**

```
SWARNE_V2/
├── swarne/
│   ├── core/              # Core system (Bee, Hive, Guardian, Field)
│   ├── backtesting/       # Backtesting engine
│   ├── ml/                # Machine Learning (LSTM)
│   ├── portfolio/         # Multi-symbol management
│   ├── dashboard/         # PyQt5 interface
│   ├── notifications/     # Telegram, Email
│   ├── database/          # Database layer
│   └── utils/             # Utilities
├── configs/               # YAML configurations
├── data/                  # Historical data, models
├── scripts/               # Launch scripts
├── tests/                 # Unit tests
└── docs/                  # Documentation
```

---

## 🚀 **INSTALLATION**

### **Prérequis**
```bash
Python 3.8+
MetaTrader 5
CUDA Toolkit 11.8+ (optionnel, pour GPU)
```

### **Installation des dépendances**
```bash
# Cloner le projet
git clone https://github.com/swarne/swarne-v2
cd swarne-v2

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer dépendances
pip install -r requirements_v2.txt

# Installation optionnelle TA-Lib
# Linux:
sudo apt-get install ta-lib
# Mac:
brew install ta-lib
# Windows: télécharger depuis https://www.ta-lib.org/
```

---

## ⚙️ **CONFIGURATION**

### **1. Fichier config_v2.yaml**

```yaml
capital:
  initial_capital: 10000.0
  max_daily_loss_pct: 3.0

swarm:
  num_bees: 20
  
genetics:
  selection_method: "tournament"
  crossover_method: "blend"
  mutation_method: "adaptive"

ml:
  enabled: true
  model_type: "lstm"
  sequence_length: 60

notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_TOKEN"
    chat_id: "YOUR_CHAT_ID"
```

### **2. Créer un Bot Telegram**

1. Parler à @BotFather sur Telegram
2. Créer un nouveau bot: `/newbot`
3. Copier le token
4. Obtenir votre chat_id: `/start` à @userinfobot
5. Mettre les valeurs dans config_v2.yaml

---

## 🎮 **UTILISATION**

### **1. Lancer le Dashboard**

```bash
python run_dashboard.py
```

Interface graphique avec :
- Métriques en temps réel
- Graphique d'equity
- Visualisation de l'essaim
- Contrôles start/stop

### **2. Lancer un Backtest**

```bash
python run_backtest.py --start 2023-01-01 --end 2024-12-16
```

Options :
- `--symbols EURUSD,GBPUSD` : Symboles à backtester
- `--capital 10000` : Capital initial
- `--output report.html` : Fichier de rapport

### **3. Entraîner un Modèle ML**

```bash
python train_ml_model.py --symbol EURUSD --epochs 50
```

Le modèle sera sauvegardé dans `data/models/`

### **4. Mode Live (avec MT5)**

```python
from swarne.core.hive import Hive
from swarne.ml.lstm_predictor import LSTMPredictor
import yaml

# Charger config
with open('configs/config_v2.yaml') as f:
    config = yaml.safe_load(f)

# Créer la Hive
hive = Hive(
    initial_capital=config['capital']['initial_capital'],
    num_bees=config['swarm']['num_bees'],
    symbols=config['trading']['symbols']
)

# Charger modèle ML
ml_model = LSTMPredictor.load('data/models/lstm_eurusd.h5')

# Lancer
while True:
    hive.run_cycle(ml_predictor=ml_model)
    time.sleep(60)
```

---

## 📊 **BACKTESTING**

### **Métriques Calculées**

- **Performance**: Total Return, Win Rate, Profit Factor
- **Risk**: Max Drawdown, Sharpe Ratio, Sortino Ratio, Calmar Ratio
- **Statistics**: Avg Trade, Largest Win/Loss, Trade Duration

### **Walk-Forward Analysis**

Validation robuste avec périodes train/test glissantes :

```python
from swarne.backtesting.engine import WalkForwardAnalysis

wfa = WalkForwardAnalysis(
    train_period_days=180,
    test_period_days=60
)

results = wfa.run(
    start_date="2023-01-01",
    end_date="2024-12-16",
    hive=hive
)
```

---

## 🧬 **GÉNÉTIQUE AVANCÉE**

### **Méthodes de Sélection**

1. **Tournament** (recommandé)
   - Compétition entre N individus
   - Meilleur équilibre exploration/exploitation

2. **Roulette**
   - Probabilité proportionnelle au fitness
   - Favorise les meilleurs

3. **Rank**
   - Basé sur le rang, pas le fitness absolu
   - Évite la domination d'un super-individu

### **Méthodes de Crossover**

1. **Blend (BLX-alpha)** (recommandé)
   - Génère enfants dans intervalle étendu
   - Excellente exploration

2. **Arithmetic**
   - Moyenne pondérée des parents
   - Stable et prévisible

3. **Uniform**
   - Chaque gène a 50% de chance
   - Haute diversité

### **Mutation Adaptative**

Le taux de mutation diminue au fil des générations :
- Début: 30% (exploration)
- Fin: 5% (exploitation fine)

---

## 🤖 **MACHINE LEARNING**

### **Architecture LSTM**

```
Input (60 x N features)
    ↓
LSTM Layer 1 (128 units) + Dropout (0.2)
    ↓
LSTM Layer 2 (64 units) + Dropout (0.2)
    ↓
LSTM Layer 3 (32 units)
    ↓
Dense Layer (32 units, ReLU)
    ↓
Output (3 classes: BUY, SELL, HOLD)
```

### **Features Utilisées**

- Prix: close, open, high, low
- Volume
- Indicateurs: EMA (9, 21, 50), RSI, ADX, ATR, MACD
- Bollinger Bands
- Momentum, ROC

### **Entraînement**

```python
from swarne.ml.lstm_predictor import LSTMPredictor, LSTMConfig

config = LSTMConfig(
    sequence_length=60,
    lstm_units=[128, 64, 32],
    epochs=50,
    batch_size=32
)

predictor = LSTMPredictor(config)
predictor.train(historical_data)
predictor.save_model('models/lstm_model.h5')
```

### **Prédiction**

```python
direction, confidence = predictor.predict(market_data)
# direction: "BUY", "SELL", ou "HOLD"
# confidence: 0.0 - 1.0
```

---

## 🌐 **MULTI-SYMBOLES**

### **Gestion de Corrélation**

Le système calcule automatiquement les corrélations entre paires :

```python
from swarne.portfolio.multi_symbol_manager import MultiSymbolManager

manager = MultiSymbolManager(['EURUSD', 'GBPUSD', 'USDJPY'])

# Vérifier risque de corrélation
risk = manager.check_correlation_risk('EURUSD')

if risk > 0.7:
    # Haute corrélation détectée
    # Réduire taille de position
    volume *= (1 - risk)
```

### **Optimisation de Portefeuille**

Allocation optimale du capital :

```python
allocation = manager.optimize_allocation(capital=10000)
# {'EURUSD': 3333, 'GBPUSD': 3333, 'USDJPY': 3334}
```

---

## 📱 **NOTIFICATIONS TELEGRAM**

### **Configuration**

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    chat_id: "123456789"
```

### **Types de Notifications**

1. **Signaux de Trading**
   - Direction (BUY/SELL)
   - Prix d'entrée
   - Confidence
   - Stop-loss / Take-profit

2. **Rapports Journaliers**
   - Capital
   - Trades du jour
   - Win rate
   - P&L

3. **Alertes**
   - Perte journalière max atteinte
   - Drawdown important
   - Nouvelle Queen bee

---

## 🎨 **DASHBOARD**

### **Fonctionnalités**

- **Métriques Live**: Capital, Bees, Trades, P&L
- **Equity Curve**: Graphique temps réel
- **Swarm Status**: État de chaque bee
- **Activity Log**: Logs détaillés
- **Controls**: Start, Stop, Refresh

### **Raccourcis Clavier**

- `Ctrl+S`: Start trading
- `Ctrl+X`: Stop trading
- `Ctrl+R`: Refresh
- `Ctrl+Q`: Quit

---

## 🧪 **TESTS**

### **Lancer les Tests**

```bash
# Tous les tests
pytest tests/

# Tests spécifiques
pytest tests/test_bee.py
pytest tests/test_backtesting.py
pytest tests/test_ml.py

# Avec coverage
pytest --cov=swarne tests/
```

---

## 📈 **RÉSULTATS ATTENDUS**

### **Performance Cible (Backtest)**

- Return annuel: 30-50%
- Sharpe Ratio: > 2.0
- Max Drawdown: < 15%
- Win Rate: 60-70%

### **Évolution de l'Essaim**

```
Generation 0  → Avg Fitness: 0.45
Generation 10 → Avg Fitness: 0.62
Generation 20 → Avg Fitness: 0.74
Generation 50 → Avg Fitness: 0.89  🚀
```

---

## 🛡️ **SÉCURITÉ**

### **Risques à Connaître**

⚠️ **Le trading automatisé comporte des risques**
- Testez TOUJOURS en démo d'abord (min 1 mois)
- Commencez avec un petit capital
- Surveillez régulièrement
- Ayez un plan d'urgence (stop-loss global)

### **Bonnes Pratiques**

✅ Backtest sur minimum 1 an de données
✅ Walk-forward analysis obligatoire
✅ Diversification multi-symboles
✅ Limites de risque strictes
✅ Logs détaillés activés
✅ Notifications en temps réel

---

## 🔧 **TROUBLESHOOTING**

### **Problème: LSTM ne converge pas**

```python
# Réduire learning rate
config.learning_rate = 0.0001

# Augmenter epochs
config.epochs = 100

# Simplifier architecture
config.lstm_units = [64, 32]
```

### **Problème: Haute corrélation entre positions**

```python
# Activer réduction automatique
hive.guardian.enable_correlation_adjustment = True

# Réduire nombre de symboles
symbols = ['EURUSD', 'USDJPY']  # Faible corrélation
```

### **Problème: Dashboard lent**

```python
# Augmenter intervalle de mise à jour
dashboard.update_interval = 5000  # 5 secondes
```

---

## 🗺️ **ROADMAP**

### **V2.1 (Q1 2025)**
- [ ] Support PostgreSQL/MongoDB
- [ ] API REST (FastAPI)
- [ ] Interface web (Streamlit)
- [ ] Transformers pour prédiction
- [ ] Sentiment analysis (Twitter, News)

### **V2.2 (Q2 2025)**
- [ ] Multi-broker (Interactive Brokers, Binance)
- [ ] Cloud deployment (AWS, Azure)
- [ ] Reinforcement Learning (DQN, PPO)
- [ ] Stratégie marketplace
- [ ] Mobile app

### **V3.0 (Q3 2025)**
- [ ] DAO governance
- [ ] NFT strategies
- [ ] Yield farming integration
- [ ] Community rewards

---

## 🤝 **CONTRIBUTION**

### **Comment Contribuer**

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### **Guidelines**

- Code formaté avec Black
- Tests pour nouvelles features
- Documentation mise à jour
- Respect des conventions

---

## 📞 **SUPPORT**

- **GitHub Issues**: https://github.com/swarne/swarne-v2/issues
- **Discord**: https://discord.gg/swarne
- **Twitter**: @SwarneAI
- **Email**: support@swarne.ai

---

## 📄 **LICENSE**

MIT License - Voir LICENSE file

---

## 🙏 **REMERCIEMENTS**

- Communauté SWARNE
- Contributors GitHub
- MetaQuotes (MT5)
- TensorFlow team
- PyQt team

---

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🐝 SWARNE V2.0 - L'ESSAIM DU FUTUR 🐝                ║
║                                                              ║
║  "L'union fait la force" - Intelligence collective          ║
║  appliquée au trading algorithmique                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**🔥 BON TRADING AVEC SWARNE V2.0 ! 🔥**
