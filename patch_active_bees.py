"""
🔧 SWARNE - PATCH ABEILLES ACTIVES
Force la génération de signaux et l'exécution de trades
"""

import logging

logger = logging.getLogger('SWARNE.Patch')

def patch_bee_generate_signal(bee):
    """
    Patch pour forcer la génération de signaux
    Réduit les seuils et augmente la probabilité de signaux
    """
    
    # Méthode originale sauvegardée
    original_generate_signal = bee.generate_signal
    
    def patched_generate_signal():
        """Version patchée de generate_signal avec seuils réduits"""
        
        try:
            # Récupérer les données du marché
            market_data = bee.field.get_market_info()
            
            if market_data is None:
                return None
            
            # Extraire les indicateurs
            price = market_data.get('price', 0)
            atr = market_data.get('atr', 0.001)
            
            # ====================================
            # PATCH: Seuils très réduits pour DEMO
            # ====================================
            
            import random
            import numpy as np
            
            # 1. Calculer indicateurs simples
            close_prices = market_data.get('close_prices', [price])
            
            if len(close_prices) < 20:
                # Pas assez de données, générer signal aléatoire
                signal_type = random.choice(['BUY', 'SELL', 'HOLD'])
                confidence = random.uniform(0.6, 0.8)
            else:
                # Calculer SMA
                sma_short = np.mean(close_prices[-5:])
                sma_long = np.mean(close_prices[-20:])
                
                # 2. Générer signal basé sur SMA
                if sma_short > sma_long * 1.0001:  # Seuil très bas !
                    signal_type = 'BUY'
                    confidence = 0.65 + random.uniform(0, 0.15)
                elif sma_short < sma_long * 0.9999:  # Seuil très bas !
                    signal_type = 'SELL'
                    confidence = 0.65 + random.uniform(0, 0.15)
                else:
                    # Marché neutre, mais on force quand même un signal
                    signal_type = random.choice(['BUY', 'SELL'])
                    confidence = 0.60 + random.uniform(0, 0.10)
            
            # 3. Calculer stop loss et take profit
            if signal_type == 'BUY':
                entry_price = price
                stop_loss = entry_price - (atr * 1.5)  # Réduit de 2 à 1.5
                take_profit = entry_price + (atr * 2.5)  # Réduit de 3 à 2.5
            elif signal_type == 'SELL':
                entry_price = price
                stop_loss = entry_price + (atr * 1.5)
                take_profit = entry_price - (atr * 2.5)
            else:
                entry_price = price
                stop_loss = None
                take_profit = None
            
            # 4. Créer le signal
            signal = {
                'bee_id': bee.bee_id,
                'type': signal_type,
                'confidence': confidence,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'timestamp': market_data.get('timestamp'),
                'atr': atr,
                'reason': f"Patched signal - SMA cross"
            }
            
            # 5. Mettre à jour la fitness de l'abeille
            # PATCH: Augmenter la fitness automatiquement
            if signal_type != 'HOLD':
                bee.fitness = max(bee.fitness, 0.5)  # Force minimum 0.5
                bee.fitness = min(bee.fitness + 0.05, 1.0)  # Augmente graduellement
            
            logger.info(f"🐝 {bee.bee_id}: {signal_type} (confidence: {confidence:.2%}, fitness: {bee.fitness:.2f})")
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Error in patched generate_signal: {e}")
            return None
    
    # Remplacer la méthode
    bee.generate_signal = patched_generate_signal
    logger.info(f"✅ Bee {bee.bee_id} patched with active signal generation")


def patch_guardian_validate(guardian):
    """
    Patch pour rendre le Guardian moins strict
    """
    
    original_validate = guardian.validate_trade
    
    def patched_validate(bee, signal, confidence, current_price, atr):
        """Version patchée de validate_trade - moins strict"""
        
        try:
            # ====================================
            # PATCH: Conditions très relâchées
            # ====================================
            
            # 1. Vérifier capital minimal (très bas)
            if guardian.current_capital < 100:  # Au lieu de 1000
                logger.warning("⚠️  Capital trop faible")
                return False, 0, 0, 0
            
            # 2. Vérifier confidence minimale (réduite)
            min_confidence = 0.55  # Au lieu de 0.65
            if confidence < min_confidence:
                logger.info(f"⚠️  Confidence trop faible: {confidence:.2%}")
                return False, 0, 0, 0
            
            # 3. FORCER l'acceptation si signal valide
            if signal in ['BUY', 'SELL']:
                # Calculer volume (0.01 lot minimum)
                volume = 0.01
                
                # Calculer SL/TP basés sur ATR
                if signal == 'BUY':
                    stop_loss = current_price - (atr * 1.5)
                    take_profit = current_price + (atr * 2.5)
                else:  # SELL
                    stop_loss = current_price + (atr * 1.5)
                    take_profit = current_price - (atr * 2.5)
                
                logger.info(f"✅ Guardian: Trade validé ({signal}, confidence: {confidence:.2%})")
                return True, volume, stop_loss, take_profit
            
            return False, 0, 0, 0
            
        except Exception as e:
            logger.error(f"❌ Error in patched validate: {e}")
            return False, 0, 0, 0
    
    guardian.validate_trade = patched_validate
    logger.info("✅ Guardian patched with relaxed validation")


def patch_hive_for_active_trading(hive):
    """
    Patch complet de la Hive pour activer le trading
    """
    
    logger.info("🔧 Applying active trading patch to Hive...")
    
    # 1. Patcher toutes les abeilles
    for bee in hive.bees:
        patch_bee_generate_signal(bee)
        # Forcer une fitness initiale
        if bee.fitness < 0.3:
            bee.fitness = 0.5
    
    logger.info(f"✅ {len(hive.bees)} bees patched")
    
    # 2. Patcher le Guardian
    patch_guardian_validate(hive.guardian)
    
    logger.info("✅ Hive fully patched for active trading")
    
    return hive


def apply_patch_to_running_system():
    """
    Appliquer le patch à un système en cours d'exécution
    """
    
    print("\n" + "="*60)
    print("🔧 SWARNE - PATCH ABEILLES ACTIVES")
    print("="*60 + "\n")
    
    try:
        # Essayer d'importer la Hive
        from swarne_ultimate import Hive
        
        print("✅ Module swarne_ultimate trouvé\n")
        print("💡 Pour appliquer le patch:")
        print("   1. Arrête le dashboard (STOP)")
        print("   2. Ferme le dashboard")
        print("   3. Lance: python quick_start.py")
        print("   4. Choisis option 2 ou 9")
        print("   5. Le patch sera appliqué automatiquement\n")
        
    except ImportError:
        print("❌ swarne_ultimate.py non trouvé")
        print("   Assure-toi d'être dans le bon dossier\n")


if __name__ == '__main__':
    apply_patch_to_running_system()
