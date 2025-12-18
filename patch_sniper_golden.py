"""
╔══════════════════════════════════════════════════════════════╗
║    PATCH: Intégration SNIPER SCOPE + GOLDENEYES → SWARNE    ║
╚══════════════════════════════════════════════════════════════╝

Ce patch intègre la vision multi-temporelle dans SWARNE
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin du module
sys.path.insert(0, str(Path(__file__).parent))

from sniper_scope_goldeneyes import (
    SniperScopeGoldenEyesIntegration,
    TimeFrame,
    SignalLevel
)

print("🎯👁️ SNIPER SCOPE + GOLDENEYES Integration Patch")
print("="*60)

# Instructions d'intégration
instructions = """
╔══════════════════════════════════════════════════════════════╗
║              INTÉGRATION DANS SWARNE                         ║
╚══════════════════════════════════════════════════════════════╝

ÉTAPE 1: Ajouter l'import dans swarne_ultimate.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

En haut du fichier, après les autres imports:

```python
from sniper_scope_goldeneyes import (
    SniperScopeGoldenEyesIntegration,
    TimeFrame
)
```

ÉTAPE 2: Initialiser dans Hive.__init__()
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ajouter après l'initialisation du Field:

```python
# 🎯👁️ Sniper Scope + GoldenEyes
self.sniper_golden = SniperScopeGoldenEyesIntegration(
    symbol=self.field.symbol,
    mt5_connection=mt5
)
logger.info("🎯👁️ Sniper Scope + GoldenEyes integrated")
```

ÉTAPE 3: Modifier run_cycle()
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Remplacer la logique de déploiement par RÔLES par:

```python
def run_cycle(self):
    logger.info(f"\\n{'='*60}")
    logger.info(f"🐝 SWARNE! - CYCLE {self.generation}")
    logger.info(f"{'='*60}")
    
    # Récupérer les données de marché
    market_data = self.field.get_market_data()
    
    if market_data.empty:
        logger.error("❌ No market data available")
        return
    
    atr = self.field.calculate_atr()
    current_price = self.field.get_current_price()
    
    logger.info(f"💰 Capital: ${self.guardian.current_capital:,.2f}")
    logger.info(f"📊 Price: {current_price:.5f} | ATR: {atr:.5f}")
    
    # ════════════════════════════════════════════════════════════
    # 🎯👁️ SNIPER SCOPE + GOLDENEYES UPDATE
    # ════════════════════════════════════════════════════════════
    
    # Préparer données multi-timeframe (optionnel)
    multi_tf_data = {
        TimeFrame.FIVE_MIN: market_data,
        # Ajouter d'autres timeframes si disponibles
    }
    
    # Obtenir recommandation complète
    recommendation = self.sniper_golden.update(market_data, multi_tf_data)
    
    # Log vision
    logger.info("")
    logger.info("🎯👁️ SNIPER SCOPE + GOLDENEYES VISION:")
    logger.info(f"  Signal: {recommendation['signal']} @ {recommendation['strength']:.1f}%")
    logger.info(f"  Precision: {recommendation['precision']:.1f}")
    logger.info(f"  Combat Readiness: {recommendation['combat_readiness']:.1f}%")
    logger.info(f"  Swarm Action: {recommendation['swarm_action']}")
    
    if recommendation['golden_vision']['global_key_moment']:
        logger.info("  👁️ GLOBAL KEY MOMENT DETECTED!")
        logger.info(f"  Dominant TF: {recommendation['golden_vision']['dominant_timeframe']}")
    
    # ════════════════════════════════════════════════════════════
    # 🐝 DÉPLOIEMENT ADAPTATIF SELON RECOMMANDATION
    # ════════════════════════════════════════════════════════════
    
    deployment = recommendation['deployment']
    
    logger.info(f"\\n🐝 Deployment: {deployment['recommended_deployment']}")
    logger.info(f"  Reason: {deployment['reason']}")
    logger.info(f"  Scouts: {deployment['scouts']}")
    logger.info(f"  Workers: {deployment['workers']}")
    logger.info(f"  Guards: {deployment['guards']}")
    
    # Calculer volatilité (pour modes adaptatifs)
    market_volatility = self._calculate_market_volatility()
    is_warrior_mode = market_volatility > 0.5
    mode_name = "⚔️ GUERRIER" if is_warrior_mode else "🌾 RÉCOLTE"
    
    total_open_positions = sum(len(bee.current_trades) for bee in self.bees)
    logger.info(f"📊 Mode: {mode_name} | Volatilité: {market_volatility:.2f} | Positions: {total_open_positions}")
    
    # ════════════════════════════════════════════════════════════
    # 🔍 PHASE 1: SCOUTS (Nombre adaptatif)
    # ════════════════════════════════════════════════════════════
    
    scouts = [bee for bee in self.bees if bee.bee_type == 'SCOUT' and bee.active]
    workers = [bee for bee in self.bees if bee.bee_type == 'WORKER' and bee.active]
    guards = [bee for bee in self.bees if bee.bee_type == 'GUARD' and bee.active]
    
    logger.info(f"🐝 Essaim: {len(scouts)} scouts, {len(workers)} workers, {len(guards)} guards actifs")
    
    # Activer le nombre de scouts recommandé
    target_scouts = deployment['scouts']
    self._activate_bees_by_type('SCOUT', target_scouts)
    
    scout_signals = []
    
    for scout in scouts[:target_scouts]:
        if len(scout.current_trades) > 0:
            continue
        
        # Générer signal (utilise recommendation['signal'])
        signal = recommendation['signal']
        confidence = recommendation['strength'] / 100.0
        
        if signal in ['BUY', 'SELL'] and confidence > 0.5:
            # Valider avec Guardian
            approved, volume, stop_loss, take_profit = self.guardian.validate_trade(
                scout, signal, confidence, current_price, atr
            )
            
            if approved:
                scout_volume = volume * 0.5  # Scouts: 50% volume
                
                logger.info(f"🔍 SCOUT {scout.bee_id} exploring: {signal} | Conf: {confidence:.0%} | Vol: {scout_volume:.2f}")
                
                ticket = self.field.place_order(signal, scout_volume, stop_loss, take_profit)
                
                if ticket:
                    trade = Trade(
                        bee_id=scout.bee_id,
                        symbol=self.field.symbol,
                        order_type=signal,
                        entry_price=current_price,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        volume=scout_volume,
                        entry_time=datetime.now(),
                        ticket=ticket
                    )
                    scout.current_trades.append(trade)
                    self.trade_history.append(trade)
                    logger.info(f"✅ SCOUT {scout.bee_id} deployed")
                    
                    scout_signals.append({'type': signal, 'confidence': confidence})
    
    # ════════════════════════════════════════════════════════════
    # 🌾 PHASE 2: WORKERS (Si scouts confirment)
    # ════════════════════════════════════════════════════════════
    
    scout_confirmed = len(scout_signals) > 0
    dominant_signal = recommendation['signal']
    
    if scout_confirmed and dominant_signal in ['BUY', 'SELL']:
        logger.info(f"🔍 SCOUTS CONFIRMED! {dominant_signal} - Sending WORKERS")
        
        # Activer workers recommandés
        target_workers = deployment['workers']
        self._activate_bees_by_type('WORKER', target_workers)
        
        for worker in workers[:target_workers]:
            if len(worker.current_trades) > 0:
                continue
            
            signal = dominant_signal
            confidence = recommendation['strength'] / 100.0
            
            if confidence > 0.5:
                approved, volume, stop_loss, take_profit = self.guardian.validate_trade(
                    worker, signal, confidence, current_price, atr
                )
                
                if approved:
                    logger.info(f"🌾 WORKER {worker.bee_id} harvesting: {signal} | Conf: {confidence:.0%} | Vol: {volume:.2f}")
                    
                    ticket = self.field.place_order(signal, volume, stop_loss, take_profit)
                    
                    if ticket:
                        trade = Trade(
                            bee_id=worker.bee_id,
                            symbol=self.field.symbol,
                            order_type=signal,
                            entry_price=current_price,
                            stop_loss=stop_loss,
                            take_profit=take_profit,
                            volume=volume,
                            entry_time=datetime.now(),
                            ticket=ticket
                        )
                        worker.current_trades.append(trade)
                        self.trade_history.append(trade)
                        logger.info(f"✅ WORKER {worker.bee_id} deployed")
    
    # ════════════════════════════════════════════════════════════
    # ⚔️ PHASE 3: GUARDS (Si moment clé majeur)
    # ════════════════════════════════════════════════════════════
    
    guards_should_attack = (
        recommendation['golden_vision']['global_key_moment'] and
        recommendation['combat_readiness'] >= 95
    )
    
    if guards_should_attack:
        logger.info(f"⚔️ GLOBAL KEY MOMENT! GUARDS ATTACK!")
        
        target_guards = deployment['guards']
        self._activate_bees_by_type('GUARD', target_guards)
        
        for guard in guards[:target_guards]:
            if len(guard.current_trades) > 0:
                continue
            
            signal = dominant_signal
            confidence = recommendation['strength'] / 100.0
            
            approved, volume, stop_loss, take_profit = self.guardian.validate_trade(
                guard, signal, confidence, current_price, atr
            )
            
            if approved:
                guard_volume = volume * 1.5  # Guards: 150% volume
                
                logger.info(f"⚔️ GUARD {guard.bee_id} attacking: {signal} | Conf: {confidence:.0%} | Vol: {guard_volume:.2f}")
                
                ticket = self.field.place_order(signal, guard_volume, stop_loss, take_profit)
                
                if ticket:
                    trade = Trade(
                        bee_id=guard.bee_id,
                        symbol=self.field.symbol,
                        order_type=signal,
                        entry_price=current_price,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        volume=guard_volume,
                        entry_time=datetime.now(),
                        ticket=ticket
                    )
                    guard.current_trades.append(trade)
                    self.trade_history.append(trade)
                    logger.info(f"✅ GUARD {guard.bee_id} deployed")
    
    # Compter positions après déploiement
    total_positions_after = sum(len(bee.current_trades) for bee in self.bees)
    
    if total_positions_after > total_open_positions:
        new_positions = total_positions_after - total_open_positions
        logger.info(f"🔥 {new_positions} nouvelles positions ouvertes!")
        
        if total_positions_after >= 15:
            logger.info(f"💥 ATTAQUE MASSIVE! {total_positions_after} positions actives!")
    
    # Mettre à jour positions ouvertes
    self._update_open_positions()
    
    # Évolution
    if self.generation % 10 == 0 and self.generation > 0:
        self._evolve_swarm()
    
    self.generation += 1
    time.sleep(1)


def _activate_bees_by_type(self, bee_type: str, target_count: int):
    \"\"\"Activer un nombre spécifique d'abeilles d'un type\"\"\"
    
    bees_of_type = [bee for bee in self.bees if bee.bee_type == bee_type]
    active_count = sum(1 for bee in bees_of_type if bee.active)
    
    if target_count > active_count:
        # Activer plus
        needed = target_count - active_count
        inactive = [bee for bee in bees_of_type if not bee.active]
        for bee in inactive[:needed]:
            bee.active = True
            logger.info(f"🐝 {bee.bee_id} ({bee_type}) activated")
    
    elif target_count < active_count:
        # Désactiver certaines
        to_deactivate = active_count - target_count
        active = [bee for bee in bees_of_type if bee.active]
        # Désactiver les moins performantes
        sorted_bees = sorted(active, key=lambda b: b.performance.fitness_score)
        for bee in sorted_bees[:to_deactivate]:
            # Fermer positions d'abord
            if bee.current_trades:
                for trade in bee.current_trades[:]:
                    self.field.close_position(trade.ticket)
            bee.active = False
            logger.info(f"🐝 {bee.bee_id} ({bee_type}) deactivated")
```

ÉTAPE 4: Tester
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```bash
python quick_start.py
```

Mode 9 → xauusd → 40

Tu devrais voir:

```
🎯👁️ SNIPER SCOPE + GOLDENEYES VISION:
  Signal: BUY @ 87.5%
  Precision: 92.3
  Combat Readiness: 94.8%
  Swarm Action: ⚡ DEPLOY ELEVATED FORCES
  👁️ GLOBAL KEY MOMENT DETECTED!
  Dominant TF: 1h

🐝 Deployment: ELEVATED
  Reason: Moment clé fort: BUY @ 87.5%
  Scouts: 4
  Workers: 15
  Guards: 4
```

╔══════════════════════════════════════════════════════════════╗
║                      AVANTAGES                               ║
╚══════════════════════════════════════════════════════════════╝

1. VISION MULTI-TEMPORELLE 👁️
   - L'essaim "voit" toutes les échelles de temps
   - Détecte les moments clés globaux
   - Adaptation intelligente

2. PRÉCISION DE SNIPER 🎯
   - Combat Readiness comme dans MQL5
   - Signal Confidence précis
   - Precision Score en temps réel

3. DÉPLOIEMENT INTELLIGENT 🐝
   - Nombre d'abeilles adaptatif
   - SCOUTS → WORKERS → GUARDS
   - Selon force du signal ET timeframes

4. COMME DANS LA NATURE ! 🌳
   - Seconde → Année → Vie entière
   - Chef d'orchestre qui voit tout
   - Réaction intelligente à chaque échelle

╔══════════════════════════════════════════════════════════════╗
║                    FICHIERS CRÉÉS                            ║
╚══════════════════════════════════════════════════════════════╝

✅ sniper_scope_goldeneyes.py   - Module complet
✅ patch_sniper_golden.py        - Ce fichier (instructions)

À FAIRE:
□ Intégrer dans swarne_ultimate.py (suivre ÉTAPE 1-3)
□ Tester avec quick_start.py
□ Observer la vision multi-temporelle
□ Profiter des moments clés ! 💰

╔══════════════════════════════════════════════════════════════╗
"""

print(instructions)

print("\n🎯👁️ Patch d'intégration prêt!")
print("\nSuis les ÉTAPES 1-4 ci-dessus pour intégrer le système.")
