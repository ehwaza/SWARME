"""
🎯 SWARNE - SNIPER SCOPE INTEGRATION AVANCÉE
Le Scope Sowilo guide l'essaim comme une abeille éclaireuse !
"""

import json
import os
import logging
from datetime import datetime

logger = logging.getLogger('SWARNE.SniperScope')

class SniperScopeIntegration:
    """Intégration avancée du Sniper Scope MT5 - Contrôle de l'essaim"""
    
    def __init__(self):
        self.signal_file = os.path.join(
            os.getenv('APPDATA', ''),
            'MetaQuotes', 'Terminal', 
            'Common', 'Files',
            'SWARNE_SNIPER_SIGNAL.json'
        )
        self.last_signal = None
        self.last_read_time = None
        self.last_strength = 0
        self.active_bees_count = 10  # Nombre d'abeilles actives par défaut
        
        logger.info("🎯 Sniper Scope Advanced Integration initialized")
    
    def read_signal(self):
        """Lire le signal du fichier JSON"""
        try:
            if not os.path.exists(self.signal_file):
                return None
            
            # Vérifier si le fichier a été modifié
            mtime = os.path.getmtime(self.signal_file)
            if self.last_read_time and mtime <= self.last_read_time:
                return self.last_signal
            
            # Lire le fichier
            with open(self.signal_file, 'r') as f:
                data = json.load(f)
            
            self.last_signal = data
            self.last_read_time = mtime
            self.last_strength = data.get('strength', 0)
            
            logger.info(f"🎯 Sniper Signal: {data['signal']} (Force: {data['strength']:.0f}%)")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error reading Sniper signal: {e}")
            return None
    
    def calculate_optimal_bee_count(self, signal_data, market_volatility=0.3):
        """
        Calculer le nombre optimal d'abeilles selon:
        - Force du signal Sniper Scope
        - Volatilité du marché
        - Mode: RÉCOLTE (calme) vs GUERRIER (volatil)
        """
        if not signal_data:
            # Sans signal, mode minimal
            return 5
        
        strength = signal_data.get('strength', 0)
        signal_type = signal_data.get('signal', 'HOLD')
        
        # Déterminer le mode selon la volatilité
        is_warrior_mode = market_volatility > 0.5
        mode_name = "⚔️ GUERRIER" if is_warrior_mode else "🌾 RÉCOLTE"
        
        # 🌾 MODE RÉCOLTE (volatilité faible, marché calme)
        if not is_warrior_mode:
            logger.info(f"🌾 MODE RÉCOLTE - Volatilité: {market_volatility:.2f}")
            
            if signal_type == 'HOLD' or strength < 50:
                return 3  # Garde minimale
            
            elif strength >= 90 and signal_type in ['BUY', 'SELL']:
                return 15  # Signal très fort, mais mode calme
            
            elif strength >= 80:
                return 12
            
            elif strength >= 70:
                return 10
            
            elif strength >= 60:
                return 7
            
            else:
                return 5  # Quelques butineuses
        
        # ⚔️ MODE GUERRIER (volatilité élevée, mouvements brusques)
        else:
            logger.info(f"⚔️ MODE GUERRIER - Volatilité: {market_volatility:.2f}")
            
            if strength >= 85 and signal_type in ['BUY', 'SELL']:
                return 40  # TOUTES LES GUERRIÈRES ! Maximum d'abeilles !
            
            elif strength >= 75 and signal_type in ['BUY', 'SELL']:
                return 30  # Grande formation d'attaque
            
            elif strength >= 65:
                return 20  # Formation moyenne
            
            elif strength >= 55:
                return 15  # Escouade réduite
            
            elif strength >= 45:
                return 10  # Patrouille
            
            else:
                return 5  # Garde de base
    
    def apply_to_hive(self, hive):
        """Appliquer les signaux du Sniper Scope à la Hive avec modes adaptatifs"""
        signal_data = self.read_signal()
        
        # Calculer la volatilité du marché
        market_volatility = self._calculate_market_volatility_for_hive(hive)
        
        if not signal_data:
            # Sans signal Sniper Scope, utiliser seulement la volatilité
            optimal_count = self.calculate_optimal_bee_count(
                {'signal': 'HOLD', 'strength': 30}, 
                market_volatility
            )
        else:
            # Avec signal Sniper Scope
            signal_type = signal_data.get('signal', 'HOLD')
            strength = signal_data.get('strength', 0)
            
            # Calculer le nombre optimal
            optimal_count = self.calculate_optimal_bee_count(signal_data, market_volatility)
        
        # Déterminer le mode
        is_warrior_mode = market_volatility > 0.5
        mode_name = "⚔️ GUERRIER" if is_warrior_mode else "🌾 RÉCOLTE"
        
        # Compter les abeilles actives
        active_bees = [bee for bee in hive.bees if bee.active]
        current_active = len(active_bees)
        
        # Compter les positions ouvertes
        total_open_positions = sum(len(bee.current_trades) for bee in hive.bees)
        
        # 🚨 RÈGLE CRITIQUE: Si blocage, forcer fermetures avant déploiement
        if total_open_positions >= 15 and optimal_count > current_active:
            logger.warning(f"🚨 BLOCAGE: {total_open_positions} positions bloquent déploiement!")
            logger.warning(f"🛡️ Libération forcée pour {mode_name}...")
            # La Hive va forcer les fermetures dans _update_open_positions
        
        if optimal_count > current_active:
            # ENVOYER plus d'abeilles !
            needed = optimal_count - current_active
            logger.info(f"🎯 {mode_name}: Deploying {needed} more bees (Volatility: {market_volatility:.2f})")
            
            inactive_bees = [bee for bee in hive.bees if not bee.active]
            for i, bee in enumerate(inactive_bees[:needed]):
                bee.active = True
                logger.info(f"🐝 {bee.bee_id} activated ({mode_name})")
        
        elif optimal_count < current_active:
            # RAPPELER des abeilles !
            to_recall = current_active - optimal_count
            logger.info(f"🎯 {mode_name}: Recalling {to_recall} bees (Volatility: {market_volatility:.2f})")
            
            # Rappeler les abeilles les moins performantes
            sorted_bees = sorted(active_bees, key=lambda b: b.performance.fitness_score)
            for i, bee in enumerate(sorted_bees[:to_recall]):
                # Fermer leurs positions d'abord
                if bee.current_trades:
                    for trade in bee.current_trades[:]:
                        logger.info(f"🐝 {bee.bee_id} recalled, closing position")
                        hive.field.close_position(trade.ticket)
                
                bee.active = False
                logger.info(f"🐝 {bee.bee_id} deactivated ({mode_name})")
        
        # 🎯 RÈGLE SOWILO: Signal fort → Forcer toutes les abeilles actives
        if signal_data and signal_data.get('strength', 0) >= 85 and signal_data.get('signal') in ['BUY', 'SELL']:
            signal_type = signal_data['signal']
            strength = signal_data['strength']
            
            logger.info(f"🔥 {mode_name} FIRE: {signal_type} @ {strength:.0f}% - FORCING {optimal_count} BEES")
            
            for bee in hive.bees[:optimal_count]:
                if not bee.active:
                    bee.active = True
                
                if hasattr(bee, 'generate_signal'):
                    # Patch temporaire du signal
                    original_generate = bee.generate_signal
                    
                    def forced_signal():
                        """Signal forcé par le Sniper Scope"""
                        return {
                            'bee_id': bee.bee_id,
                            'type': signal_type,
                            'confidence': strength,
                            'entry_price': signal_data.get('price', 0),
                            'stop_loss': signal_data.get('stop_loss', 0),
                            'take_profit': signal_data.get('profit_target', 0),
                            'timestamp': datetime.now(),
                            'reason': f"SOWILO {mode_name} @ {strength:.0f}%"
                        }
                    
                    bee.generate_signal = forced_signal
        
        self.active_bees_count = optimal_count
        
        logger.info(f"🎯 {mode_name} STATUS: {optimal_count}/{len(hive.bees)} bees active")
        logger.info(f"📊 Market: Volatility={market_volatility:.2f}, Positions={total_open_positions}")
    
    def _calculate_market_volatility_for_hive(self, hive):
        """Calculer la volatilité pour la Hive"""
        try:
            # Utiliser la méthode de la Hive si elle existe
            if hasattr(hive, '_calculate_market_volatility'):
                return hive._calculate_market_volatility()
            
            # Sinon, calcul manuel
            rates = mt5.copy_rates_from_pos(hive.field.symbol, mt5.TIMEFRAME_M1, 0, 20)
            
            if rates is None or len(rates) < 20:
                return 0.3
            
            high_low = [r['high'] - r['low'] for r in rates]
            atr = sum(high_low) / len(high_low)
            normalized_volatility = min(atr / 2.0, 1.0)
            
            return normalized_volatility
            
        except Exception as e:
            logger.error(f"❌ Error calculating volatility: {e}")
            return 0.3


def patch_hive_with_sniper_scope_advanced(hive):
    """Patcher la Hive avec l'intégration avancée du Sniper Scope"""
    
    logger.info("🎯 Patching Hive with Advanced Sniper Scope integration...")
    
    # Créer l'intégration
    sniper = SniperScopeIntegration()
    
    # Sauvegarder la méthode run_cycle originale
    original_run_cycle = hive.run_cycle
    
    def patched_run_cycle():
        """Run cycle avec intégration Sniper Scope avancée"""
        
        # 1. Lire le signal du Sniper Scope et ajuster l'essaim
        sniper.apply_to_hive(hive)
        
        # 2. Exécuter le cycle normal (seulement les abeilles actives traderont)
        original_run_cycle()
        
        # 3. Log du statut après cycle
        active_count = len([bee for bee in hive.bees if bee.active])
        trading_count = len([bee for bee in hive.bees if bee.current_trades])
        logger.info(f"📊 Cycle complete: {active_count} active, {trading_count} trading")
    
    # Remplacer la méthode
    hive.run_cycle = patched_run_cycle
    
    # Ajouter l'intégration à la Hive pour accès externe
    hive.sniper_scope = sniper
    
    logger.info("✅ Hive patched with Advanced Sniper Scope integration")
    logger.info("🎯 SOWILO will dynamically control bee deployment")
    
    return hive


if __name__ == '__main__':
    print("""
🎯 SNIPER SCOPE ADVANCED INTEGRATION
====================================

COMME LES ABEILLES ÉCLAIREUSES ! 🐝

INSTALLATION:

1. Copie SNIPER_SCOPE_SWARNE.mq5 dans:
   MT5/MQL5/Indicators/

2. Compile dans MT5 (F7)

3. Ajoute l'indicateur sur le graphique XAUUSD

4. Lance SWARNE avec cette intégration:
   
   from patch_sniper_scope import patch_hive_with_sniper_scope_advanced
   
   hive = Hive(capital=100000, num_bees=20, symbol='XAUUSD')
   hive = patch_hive_with_sniper_scope_advanced(hive)
   
   while True:
       hive.run_cycle()

FONCTIONNEMENT NATUREL:

╔════════════════════════════════════════════╗
║  FORCE SOWILO  │  ABEILLES ACTIVES        ║
╠════════════════════════════════════════════╣
║    90-100%     │  20 (TOUTES !)     🔥    ║
║    80-89%      │  15 (75%)          🚀    ║
║    70-79%      │  12 (60%)          ⚡    ║
║    60-69%      │  8  (40%)          ✅    ║
║    50-59%      │  5  (25%)          🛡️    ║
║    0-49%       │  3  (15%)          😴    ║
╚════════════════════════════════════════════╝

EXEMPLE EN ACTION:

MT5 Sniper Scope: Force 92% BUY
    ↓
🔥 SOWILO FIRE: BUY @ 92% - FORCING 20 BEES
🐝 All 20 bees deployed!
    ↓
Cycle 1-10: 20 positions BUY ouvertes
    ↓
20 secondes passent, profit accumulé
    ↓
🐝 Bees returning with nectar: 20 × €0.20 = €4.00
    ↓
MT5 Sniper Scope: Force 45% HOLD
    ↓
🛡️ SOWILO HOLD: Recalling to minimal guard
🐝 17 bees recalled, 3 guards remain
    ↓
Capital sécurisé ! Pas de surexposition !

═══════════════════════════════════════════════

LES ABEILLES NE S'ÉTERNISENT PAS !
LE SCOPE SOWILO LES GUIDE !
COMME DANS LA NATURE ! 🐝🌸

═══════════════════════════════════════════════
""")

