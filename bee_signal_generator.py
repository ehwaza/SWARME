"""
🐝 SWARNE - Générateur de Signaux pour Abeilles
Module complet pour ajouter la génération de signaux aux abeilles

Ce module contient toute la logique de trading qui manque dans swarne_ultimate.py
"""

import random
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger('SWARNE.SignalGenerator')


def add_signal_generation_to_bee(bee):
    """
    Ajouter la capacité de génération de signaux à une abeille
    
    Cette fonction ajoute la méthode generate_signal() à l'abeille
    """
    
    def generate_signal(self):
        """
        Générer un signal de trading basé sur l'analyse technique
        
        Returns:
            dict: Signal avec type, confidence, entry_price, stop_loss, take_profit
            None: Si aucun signal valide
        """
        try:
            # 0. Initialiser fitness si absent (bug dans swarne_ultimate.py)
            if not hasattr(self, 'fitness'):
                self.fitness = 0.0
            
            # 1. Récupérer les données du marché
            if not hasattr(self, 'field') or self.field is None:
                return None
            
            market_data = self.field.get_market_info()
            if market_data is None:
                return None
            
            # 2. Extraire les informations
            price = market_data.get('price', 0)
            atr = market_data.get('atr', 0.001)
            
            if price == 0 or atr == 0:
                return None
            
            # 3. Récupérer l'historique des prix
            close_prices = market_data.get('close_prices', [])
            
            if len(close_prices) < 20:
                # Pas assez de données, signal basique
                return self._generate_basic_signal(price, atr)
            
            # 4. Calculer les indicateurs techniques
            indicators = self._calculate_indicators(close_prices, price)
            
            # 5. Déterminer le type de signal
            signal_type = self._determine_signal_type(indicators)
            
            if signal_type == 'HOLD':
                return None
            
            # 6. Calculer la confidence
            confidence = self._calculate_confidence(indicators, signal_type)
            
            # Seuil minimum de confidence (relâché pour DEMO)
            if confidence < 0.55:
                return None
            
            # 7. Calculer stop loss et take profit
            if signal_type == 'BUY':
                entry_price = price
                stop_loss = entry_price - (atr * 1.5)
                take_profit = entry_price + (atr * 2.5)
            elif signal_type == 'SELL':
                entry_price = price
                stop_loss = entry_price + (atr * 1.5)
                take_profit = entry_price - (atr * 2.5)
            else:
                return None
            
            # 8. Créer le signal
            signal = {
                'bee_id': self.bee_id,
                'type': signal_type,
                'confidence': confidence,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'timestamp': datetime.now(),
                'atr': atr,
                'reason': self._get_signal_reason(indicators, signal_type)
            }
            
            # 9. Augmenter la fitness de l'abeille
            self.fitness = min(self.fitness + 0.05, 1.0)
            
            logger.info(f"🐝 {self.bee_id}: {signal_type} signal (confidence: {confidence:.2%}, fitness: {self.fitness:.2f})")
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Error generating signal for {self.bee_id}: {e}")
            return None
    
    def _generate_basic_signal(self, price, atr):
        """Générer un signal basique quand pas assez de données"""
        signal_type = random.choice(['BUY', 'SELL', 'HOLD', 'HOLD'])
        
        if signal_type == 'HOLD':
            return None
        
        confidence = random.uniform(0.55, 0.75)
        
        if signal_type == 'BUY':
            entry_price = price
            stop_loss = entry_price - (atr * 1.5)
            take_profit = entry_price + (atr * 2.5)
        else:  # SELL
            entry_price = price
            stop_loss = entry_price + (atr * 1.5)
            take_profit = entry_price - (atr * 2.5)
        
        return {
            'bee_id': self.bee_id,
            'type': signal_type,
            'confidence': confidence,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'timestamp': datetime.now(),
            'atr': atr,
            'reason': 'Basic signal (insufficient data)'
        }
    
    def _calculate_indicators(self, close_prices, current_price):
        """Calculer les indicateurs techniques"""
        indicators = {}
        
        try:
            # SMA (Simple Moving Average)
            indicators['sma_5'] = np.mean(close_prices[-5:])
            indicators['sma_10'] = np.mean(close_prices[-10:])
            indicators['sma_20'] = np.mean(close_prices[-20:])
            
            # Tendance
            if indicators['sma_5'] > indicators['sma_20']:
                indicators['trend'] = 'UP'
            elif indicators['sma_5'] < indicators['sma_20']:
                indicators['trend'] = 'DOWN'
            else:
                indicators['trend'] = 'NEUTRAL'
            
            # Distance par rapport aux SMA
            indicators['distance_sma_5'] = (current_price - indicators['sma_5']) / indicators['sma_5']
            indicators['distance_sma_20'] = (current_price - indicators['sma_20']) / indicators['sma_20']
            
            # Momentum (différence entre SMA courtes et longues)
            indicators['momentum'] = (indicators['sma_5'] - indicators['sma_20']) / indicators['sma_20']
            
            # RSI simple (basé sur les 14 dernières barres)
            if len(close_prices) >= 14:
                changes = np.diff(close_prices[-14:])
                gains = np.where(changes > 0, changes, 0)
                losses = np.where(changes < 0, -changes, 0)
                
                avg_gain = np.mean(gains) if len(gains) > 0 else 0
                avg_loss = np.mean(losses) if len(losses) > 0 else 0
                
                if avg_loss == 0:
                    indicators['rsi'] = 100
                else:
                    rs = avg_gain / avg_loss
                    indicators['rsi'] = 100 - (100 / (1 + rs))
            else:
                indicators['rsi'] = 50  # Neutre
            
            # Volatilité (écart-type des 20 dernières barres)
            indicators['volatility'] = np.std(close_prices[-20:]) / np.mean(close_prices[-20:])
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            # Valeurs par défaut en cas d'erreur
            indicators = {
                'sma_5': current_price,
                'sma_10': current_price,
                'sma_20': current_price,
                'trend': 'NEUTRAL',
                'distance_sma_5': 0,
                'distance_sma_20': 0,
                'momentum': 0,
                'rsi': 50,
                'volatility': 0.01
            }
        
        return indicators
    
    def _determine_signal_type(self, indicators):
        """Déterminer le type de signal (BUY/SELL/HOLD)"""
        
        score = 0
        
        # 1. Tendance (poids: 3)
        if indicators['trend'] == 'UP':
            score += 3
        elif indicators['trend'] == 'DOWN':
            score -= 3
        
        # 2. Momentum (poids: 2)
        if indicators['momentum'] > 0.001:  # Seuil réduit pour DEMO
            score += 2
        elif indicators['momentum'] < -0.001:
            score -= 2
        
        # 3. RSI (poids: 2)
        if indicators['rsi'] < 35:  # Survente
            score += 2
        elif indicators['rsi'] > 65:  # Surachat
            score -= 2
        
        # 4. Distance SMA (poids: 1)
        if indicators['distance_sma_20'] < -0.002:  # En dessous de SMA
            score += 1
        elif indicators['distance_sma_20'] > 0.002:  # Au dessus de SMA
            score -= 1
        
        # Décision basée sur le score
        if score >= 3:  # Seuil réduit de 4 à 3
            return 'BUY'
        elif score <= -3:  # Seuil réduit de -4 à -3
            return 'SELL'
        else:
            return 'HOLD'
    
    def _calculate_confidence(self, indicators, signal_type):
        """Calculer la confidence du signal (0-1)"""
        
        confidence = 0.5  # Base
        
        # 1. Force de la tendance
        if indicators['trend'] == signal_type.replace('BUY', 'UP').replace('SELL', 'DOWN'):
            confidence += 0.15
        
        # 2. Alignement momentum
        if signal_type == 'BUY' and indicators['momentum'] > 0:
            confidence += 0.10
        elif signal_type == 'SELL' and indicators['momentum'] < 0:
            confidence += 0.10
        
        # 3. RSI dans zone appropriée
        if signal_type == 'BUY' and indicators['rsi'] < 45:
            confidence += 0.10
        elif signal_type == 'SELL' and indicators['rsi'] > 55:
            confidence += 0.10
        
        # 4. Volatilité modérée (ni trop haute ni trop basse)
        if 0.005 < indicators['volatility'] < 0.03:
            confidence += 0.10
        
        # 5. Ajouter un peu d'aléatoire (variation génétique)
        confidence += random.uniform(-0.05, 0.05)
        
        # Limiter entre 0.5 et 0.95
        confidence = max(0.5, min(0.95, confidence))
        
        return confidence
    
    def _get_signal_reason(self, indicators, signal_type):
        """Obtenir une explication du signal"""
        reasons = []
        
        if indicators['trend'] == 'UP':
            reasons.append("Trend UP")
        elif indicators['trend'] == 'DOWN':
            reasons.append("Trend DOWN")
        
        if abs(indicators['momentum']) > 0.001:
            reasons.append(f"Momentum: {indicators['momentum']:.4f}")
        
        if indicators['rsi'] < 35:
            reasons.append("RSI oversold")
        elif indicators['rsi'] > 65:
            reasons.append("RSI overbought")
        
        return " | ".join(reasons) if reasons else "Technical analysis"
    
    # Initialiser fitness si absent (bug dans swarne_ultimate.py)
    if not hasattr(bee, 'fitness'):
        bee.fitness = 0.0
    
    # Attacher les méthodes à l'abeille
    bee.generate_signal = generate_signal.__get__(bee, bee.__class__)
    bee._generate_basic_signal = _generate_basic_signal.__get__(bee, bee.__class__)
    bee._calculate_indicators = _calculate_indicators.__get__(bee, bee.__class__)
    bee._determine_signal_type = _determine_signal_type.__get__(bee, bee.__class__)
    bee._calculate_confidence = _calculate_confidence.__get__(bee, bee.__class__)
    bee._get_signal_reason = _get_signal_reason.__get__(bee, bee.__class__)
    
    logger.debug(f"✅ Signal generation added to {bee.bee_id} (fitness: {bee.fitness})")


def patch_hive_with_signal_generation(hive):
    """
    Patcher toute la Hive pour ajouter la génération de signaux
    
    Args:
        hive: Instance de Hive
    
    Returns:
        hive: Hive modifiée
    """
    logger.info("🔧 Adding signal generation to all bees...")
    
    for bee in hive.bees:
        add_signal_generation_to_bee(bee)
    
    logger.info(f"✅ Signal generation added to {len(hive.bees)} bees")
    
    return hive


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🐝 SWARNE - Générateur de Signaux")
    print("="*60 + "\n")
    
    print("Ce module ajoute la génération de signaux aux abeilles.")
    print("\nUtilisation:")
    print("  from bee_signal_generator import patch_hive_with_signal_generation")
    print("  hive = patch_hive_with_signal_generation(hive)")
    print("\n")
