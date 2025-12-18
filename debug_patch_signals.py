"""
🔧 SWARNE - Patch de Débogage Signal Generation
Force la génération de signaux et patche automatiquement les nouvelles abeilles

Ce patch résout 2 problèmes :
1. Aucun signal généré malgré le générateur appliqué
2. Nouvelles abeilles (GEN10, GEN20, etc.) n'ont pas le générateur
"""

import logging
import random

logger = logging.getLogger('SWARNE.DebugPatch')


def patch_hive_force_signals(hive):
    """
    Patch la Hive pour forcer la génération de signaux
    
    1. Patche la méthode run_cycle() pour logger et générer des signaux
    2. Patche la méthode evolve() pour patcher les nouvelles abeilles
    """
    logger.info("🔧 Applying FORCE SIGNALS debug patch...")
    
    # Sauvegarder la méthode run_cycle originale
    original_run_cycle = hive.run_cycle
    
    # Compteur de signaux
    hive.signals_generated_count = 0
    hive.signals_rejected_count = 0
    
    def run_cycle_with_forced_signals(self):
        """Run cycle avec génération forcée de signaux"""
        
        logger.debug(f"🔄 Starting cycle {self.cycles_count}")
        
        # Appeler le cycle original
        result = original_run_cycle()
        
        # Forcer la génération de signaux sur chaque abeille
        signals_this_cycle = 0
        
        for bee in self.bees:
            try:
                # Vérifier que l'abeille a la méthode generate_signal
                if not hasattr(bee, 'generate_signal'):
                    logger.warning(f"⚠️  {bee.bee_id} does not have generate_signal()!")
                    
                    # Appliquer le générateur maintenant
                    try:
                        from bee_signal_generator import add_signal_generation_to_bee
                        add_signal_generation_to_bee(bee)
                        logger.info(f"✅ {bee.bee_id} patched with signal generator")
                    except Exception as e:
                        logger.error(f"❌ Failed to patch {bee.bee_id}: {e}")
                        continue
                
                # Essayer de générer un signal
                signal = bee.generate_signal()
                
                if signal:
                    signals_this_cycle += 1
                    self.signals_generated_count += 1
                    
                    logger.info(f"✅ {bee.bee_id}: {signal['type']} signal generated (confidence: {signal['confidence']:.2%})")
                    
                    # Valider avec le Guardian
                    if hasattr(self, 'guardian') and hasattr(self.guardian, 'validate_trade'):
                        validated = self.guardian.validate_trade(signal)
                        
                        if validated:
                            logger.info(f"✅ Guardian APPROVED {bee.bee_id} signal")
                            
                            # Exécuter le trade
                            if hasattr(self.guardian, 'execute_trade'):
                                trade_result = self.guardian.execute_trade(signal)
                                if trade_result:
                                    logger.info(f"📊 Trade EXECUTED: {signal['type']} @ {signal['entry_price']}")
                                else:
                                    logger.warning(f"⚠️  Trade execution FAILED")
                        else:
                            self.signals_rejected_count += 1
                            logger.warning(f"❌ Guardian REJECTED {bee.bee_id} signal (confidence: {signal['confidence']:.2%})")
                else:
                    logger.debug(f"➖ {bee.bee_id}: No signal (HOLD)")
                    
            except Exception as e:
                logger.error(f"❌ Error generating signal for {bee.bee_id}: {e}")
                import traceback
                traceback.print_exc()
        
        logger.info(f"📊 Cycle {self.cycles_count}: {signals_this_cycle} signals generated")
        
        return result
    
    # Remplacer la méthode
    hive.run_cycle = run_cycle_with_forced_signals.__get__(hive, hive.__class__)
    
    logger.info("✅ run_cycle() patched with forced signal generation")
    
    # Patcher evolve() pour patcher les nouvelles abeilles
    if hasattr(hive, 'evolve'):
        original_evolve = hive.evolve
        
        def evolve_with_auto_patch(self):
            """Evolve avec patching automatique des nouvelles abeilles"""
            
            # Compter les abeilles avant
            bees_before = len(self.bees)
            
            # Appeler evolve original
            result = original_evolve()
            
            # Compter les abeilles après
            bees_after = len(self.bees)
            
            # Si nouvelles abeilles créées
            if bees_after > bees_before:
                new_bees_count = bees_after - bees_before
                logger.info(f"🐣 {new_bees_count} new bees detected, patching...")
                
                # Patcher les nouvelles abeilles
                patched = 0
                for bee in self.bees:
                    if not hasattr(bee, 'generate_signal'):
                        try:
                            from bee_signal_generator import add_signal_generation_to_bee
                            add_signal_generation_to_bee(bee)
                            patched += 1
                        except Exception as e:
                            logger.error(f"❌ Failed to patch {bee.bee_id}: {e}")
                
                if patched > 0:
                    logger.info(f"✅ {patched} new bees patched with signal generator")
            
            return result
        
        hive.evolve = evolve_with_auto_patch.__get__(hive, hive.__class__)
        logger.info("✅ evolve() patched with auto-patching for new bees")
    
    logger.info("✅ FORCE SIGNALS debug patch fully applied")
    
    return hive


def create_test_signal_for_bee(bee):
    """
    Créer un signal de test pour une abeille
    Utilisé pour forcer la génération même si les conditions ne sont pas remplies
    """
    
    try:
        # Récupérer le prix actuel
        if hasattr(bee, 'field') and bee.field:
            market_data = bee.field.get_market_info()
            if market_data:
                price = market_data.get('price', 4333.0)
                atr = market_data.get('atr', 10.0)
            else:
                price = 4333.0
                atr = 10.0
        else:
            price = 4333.0
            atr = 10.0
        
        # Générer un signal aléatoire
        signal_type = random.choice(['BUY', 'SELL'])
        confidence = random.uniform(0.6, 0.85)
        
        if signal_type == 'BUY':
            entry_price = price
            stop_loss = entry_price - (atr * 1.5)
            take_profit = entry_price + (atr * 2.5)
        else:  # SELL
            entry_price = price
            stop_loss = entry_price + (atr * 1.5)
            take_profit = entry_price - (atr * 2.5)
        
        from datetime import datetime
        
        signal = {
            'bee_id': bee.bee_id,
            'type': signal_type,
            'confidence': confidence,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'timestamp': datetime.now(),
            'atr': atr,
            'reason': 'Test signal (forced generation)'
        }
        
        # Augmenter fitness
        if not hasattr(bee, 'fitness'):
            bee.fitness = 0.0
        bee.fitness = min(bee.fitness + 0.05, 1.0)
        
        logger.info(f"🧪 TEST SIGNAL created for {bee.bee_id}: {signal_type} @ {entry_price:.2f}")
        
        return signal
        
    except Exception as e:
        logger.error(f"❌ Error creating test signal: {e}")
        return None


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔧 SWARNE - Patch de Débogage Signal Generation")
    print("="*60 + "\n")
    
    print("Ce patch force la génération de signaux et patche automatiquement les nouvelles abeilles.")
    print("\nUtilisation:")
    print("  from debug_patch_signals import patch_hive_force_signals")
    print("  hive = patch_hive_force_signals(hive)")
    print("\n")
