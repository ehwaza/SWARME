"""
╔══════════════════════════════════════════════════════════════╗
║           SNIPER SCOPE + GOLDENEYES INTEGRATION              ║
║                   Vision Multi-Temporelle                    ║
╚══════════════════════════════════════════════════════════════╝

Adapté du SNIPER_SCOPE.mq5 pour Python
Intégration avec SWARNE pour vision intelligente
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("SNIPER_SCOPE")


class TimeFrame(Enum):
    """Échelles de temps pour GOLDENEYES"""
    SECOND = "1s"      # Scalping ultra-rapide
    MINUTE = "1m"      # Momentum immédiat
    FIVE_MIN = "5m"    # Scalping standard
    FIFTEEN_MIN = "15m"  # Court terme
    HOUR = "1h"        # Tendance horaire
    FOUR_HOUR = "4h"   # Structure intraday
    DAY = "1d"         # Structure quotidienne
    WEEK = "1w"        # Cycle hebdomadaire
    MONTH = "1M"       # Saison mensuelle
    YEAR = "1y"        # Macro annuel


class SignalLevel(Enum):
    """Niveaux de signal du Sniper Scope"""
    DISABLED = 0
    WAIT = 1
    HOLD = 2
    WATCH = 3
    READY = 4
    FIRE = 5
    STANDBY = 6
    HOLD_FIRE = 7
    WATCH_CLOSE = 8
    COMBAT_READY = 9
    FIRE_NOW = 10


@dataclass
class SniperMetrics:
    """Métriques du Sniper Scope (comme dans MQL5)"""
    market_tension: float = 0.0         # 0-100
    signal_confidence: float = 0.0      # 0-100
    signal_strength: float = 0.0        # 0-100
    precision_score: float = 0.0        # 0-100
    combat_readiness: float = 0.0       # 0-100
    gold_momentum: float = 0.0          # Momentum or
    gold_bias_strength: float = 0.0     # Force du biais
    current_signal: str = "HOLD"
    signal_level: SignalLevel = SignalLevel.HOLD
    market_bias: str = "NEUTRAL"        # BUY/SELL/NEUTRAL


@dataclass
class GoldenEye:
    """Un Œil d'Or pour une échelle de temps"""
    timeframe: TimeFrame
    importance: float               # 0-1 (importance de cette échelle)
    last_key_moment: datetime = None
    key_moments_detected: int = 0
    signal_strength: float = 0.0
    trend_direction: str = "NEUTRAL"
    momentum: float = 0.0
    volatility: float = 0.0
    is_active: bool = True


class SniperScope:
    """
    Sniper Scope - Adapté du MQL5
    
    Calcule les métriques de précision pour le trading:
    - Market Tension
    - Signal Confidence
    - Combat Readiness
    - Precision Score
    """
    
    def __init__(self, symbol: str, mt5_connection):
        self.symbol = symbol
        self.mt5 = mt5_connection
        
        # Configuration (comme dans MQL5)
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        
        self.ma_period = 50
        self.fast_ma_period = 5  # Pour scalping
        
        self.stoch_k = 5
        self.stoch_d = 3
        self.stoch_slowing = 3
        
        # Gold specific
        self.gold_mode = symbol == "XAUUSD"
        self.gold_volatility_multiplier = 1.5
        self.gold_pip_target = 10.0
        self.gold_stop_loss = 15.0
        
        # Scalping
        self.scalp_mode = True
        self.scalp_signal_period = 5
        self.scalp_volatility_threshold = 0.3
        self.auto_fire_strength = 85
        
        # État
        self.metrics = SniperMetrics()
        self.last_update = datetime.now()
        
        # Performance tracking (comme MQL5)
        self.total_signals = 0
        self.buy_signals = 0
        self.sell_signals = 0
        self.successful_signals = 0
        
        logger.info(f"🎯 SNIPER SCOPE initialized for {symbol}")
        if self.gold_mode:
            logger.info("🥇 GOLD MODE activated")
    
    def update(self, market_data: pd.DataFrame) -> SniperMetrics:
        """
        Mettre à jour toutes les métriques du Sniper Scope
        
        Comme OnCalculate() dans MQL5
        """
        if market_data.empty:
            return self.metrics
        
        try:
            # 1. Update market data
            current_price = market_data['close'].iloc[-1]
            
            # 2. Calculate trading metrics
            self._calculate_trading_metrics(market_data)
            
            # 3. Determine trading signal
            self._determine_trading_signal(market_data)
            
            # 4. Calculate precision score
            self._update_precision_score()
            
            self.last_update = datetime.now()
            
            return self.metrics
            
        except Exception as e:
            logger.error(f"❌ Error updating Sniper Scope: {e}")
            return self.metrics
    
    def _calculate_trading_metrics(self, market_data: pd.DataFrame):
        """Calculer les métriques de trading (comme dans MQL5)"""
        
        # Market Tension (volatilité + spread)
        market_volatility = self._calculate_volatility(market_data)
        spread_factor = 0.1  # Simplifié
        
        volatility_factor = min(market_volatility * 15, 100)
        spread_factor_norm = min(spread_factor * 10000, 50)
        self.metrics.market_tension = (volatility_factor + spread_factor_norm) / 2
        
        # Gold specific adjustment
        if self.gold_mode:
            market_volatility *= self.gold_volatility_multiplier
        
        # Signal Confidence (indicators)
        self.metrics.signal_confidence = self._calculate_indicator_confidence(market_data)
        
        # Signal Strength
        self.metrics.signal_strength = (
            self.metrics.market_tension * 0.3 + 
            self.metrics.signal_confidence * 0.7
        )
        self.metrics.signal_strength = max(0, min(100, self.metrics.signal_strength))
        
        # Combat Readiness (pour scalping)
        self.metrics.combat_readiness = (
            self.metrics.signal_confidence * (1 + market_volatility / 100)
        )
        self.metrics.combat_readiness = min(100, self.metrics.combat_readiness)
        
        # Gold momentum
        if self.gold_mode:
            self._calculate_gold_momentum(market_data)
    
    def _calculate_indicator_confidence(self, market_data: pd.DataFrame) -> float:
        """Calculer la confiance depuis les indicateurs (comme MQL5)"""
        
        confidence = 50.0
        total_weight = 0
        
        # RSI confidence
        rsi = self._calculate_rsi(market_data, self.rsi_period)
        if not np.isnan(rsi):
            rsi_score = 100 - abs(rsi - 50) * 2
            confidence += rsi_score * 0.3
            total_weight += 0.3
        
        # MACD confidence
        macd_line, signal_line = self._calculate_macd(market_data)
        if len(macd_line) > 0 and len(signal_line) > 0:
            macd_val = macd_line.iloc[-1]
            signal_val = signal_line.iloc[-1]
            if not np.isnan(macd_val) and not np.isnan(signal_val):
                macd_trend = abs(macd_val - signal_val) * 1000
                macd_score = min(macd_trend, 100)
                confidence += macd_score * 0.3
                total_weight += 0.3
        
        # Fast MA (scalping)
        if self.scalp_mode:
            fast_ma = market_data['close'].rolling(self.fast_ma_period).mean()
            if len(fast_ma) >= 2:
                current_price = market_data['close'].iloc[-1]
                price_above_ma = 1 if current_price > fast_ma.iloc[-1] else -1
                prev_price_above_ma = 1 if market_data['close'].iloc[-2] > fast_ma.iloc[-2] else -1
                
                if price_above_ma == prev_price_above_ma:
                    confidence += 25 * 0.2
                total_weight += 0.2
        
        # Stochastic (scalping)
        if self.scalp_mode:
            stoch_k, stoch_d = self._calculate_stochastic(market_data)
            if not np.isnan(stoch_k) and not np.isnan(stoch_d):
                if stoch_k > 80 and stoch_d > 80:
                    confidence += 30 * 0.2
                elif stoch_k < 20 and stoch_d < 20:
                    confidence += 30 * 0.2
                total_weight += 0.2
        
        # Normalize
        if total_weight > 0:
            confidence = confidence / total_weight
        
        return max(0, min(100, confidence))
    
    def _determine_trading_signal(self, market_data: pd.DataFrame):
        """Déterminer le signal de trading (comme MQL5)"""
        
        market_bias = "NEUTRAL"
        bias_color = "WHITE"
        strong_bias = False
        
        # Scalping mode: fast indicators
        if self.scalp_mode:
            # Check fast MA for bias
            fast_ma = market_data['close'].rolling(self.fast_ma_period).mean()
            if len(fast_ma) >= 2:
                current_price = market_data['close'].iloc[-1]
                
                if (current_price > fast_ma.iloc[-1] and 
                    fast_ma.iloc[-1] > fast_ma.iloc[-2]):
                    market_bias = "BUY"
                    strong_bias = True
                elif (current_price < fast_ma.iloc[-1] and 
                      fast_ma.iloc[-1] < fast_ma.iloc[-2]):
                    market_bias = "SELL"
                    strong_bias = True
            
            # MACD crossover
            if not strong_bias:
                macd_line, signal_line = self._calculate_macd(market_data)
                if len(market_data) >= 3:
                    # Recent crossover check
                    for i in range(2):
                        idx = -(i+1)
                        prev_idx = -(i+2)
                        if (macd_line.iloc[idx] < signal_line.iloc[idx] and 
                            macd_line.iloc[prev_idx] > signal_line.iloc[prev_idx]):
                            market_bias = "BUY"
                            break
                        elif (macd_line.iloc[idx] > signal_line.iloc[idx] and 
                              macd_line.iloc[prev_idx] < signal_line.iloc[prev_idx]):
                            market_bias = "SELL"
                            break
            
            # Force bias if very high confidence
            if market_bias == "NEUTRAL" and self.metrics.signal_confidence > 90:
                # Price action
                if len(market_data) >= 2:
                    if (market_data['close'].iloc[-1] > market_data['open'].iloc[-1] and
                        market_data['close'].iloc[-2] > market_data['open'].iloc[-2]):
                        market_bias = "BUY"
                    elif (market_data['close'].iloc[-1] < market_data['open'].iloc[-1] and
                          market_data['close'].iloc[-2] < market_data['open'].iloc[-2]):
                        market_bias = "SELL"
        
        else:
            # Standard mode
            rsi = self._calculate_rsi(market_data, self.rsi_period)
            if len(market_data) >= 2:
                rsi_prev = self._calculate_rsi(market_data.iloc[:-1], self.rsi_period)
                
                if rsi < self.rsi_oversold and rsi_prev < self.rsi_oversold:
                    market_bias = "BUY"
                    strong_bias = True
                elif rsi > self.rsi_overbought and rsi_prev > self.rsi_overbought:
                    market_bias = "SELL"
                    strong_bias = True
            
            if not strong_bias:
                macd_line, signal_line = self._calculate_macd(market_data)
                if len(macd_line) >= 2:
                    if (macd_line.iloc[-2] < signal_line.iloc[-2] and 
                        macd_line.iloc[-1] > signal_line.iloc[-1]):
                        market_bias = "BUY"
                    elif (macd_line.iloc[-2] > signal_line.iloc[-2] and 
                          macd_line.iloc[-1] < signal_line.iloc[-1]):
                        market_bias = "SELL"
        
        self.metrics.market_bias = market_bias
        
        # Determine signal level
        if self.scalp_mode:
            # Scalping: aggressive signals
            if (self.metrics.signal_strength >= 90 and 
                self.metrics.combat_readiness >= 95 and 
                market_bias != "NEUTRAL"):
                self.metrics.current_signal = "FIRE NOW!"
                self.metrics.signal_level = SignalLevel.FIRE_NOW
                
                if market_bias == "BUY":
                    self.buy_signals += 1
                else:
                    self.sell_signals += 1
                self.total_signals += 1
                
            elif (self.metrics.signal_strength >= 80 and 
                  self.metrics.combat_readiness >= 85):
                self.metrics.current_signal = "COMBAT READY"
                self.metrics.signal_level = SignalLevel.COMBAT_READY
                
            elif self.metrics.signal_strength >= 70:
                self.metrics.current_signal = "WATCH CLOSE"
                self.metrics.signal_level = SignalLevel.WATCH_CLOSE
                
            elif self.metrics.signal_strength >= 50:
                self.metrics.current_signal = "HOLD FIRE"
                self.metrics.signal_level = SignalLevel.HOLD_FIRE
                
            else:
                self.metrics.current_signal = "STANDBY"
                self.metrics.signal_level = SignalLevel.STANDBY
        
        else:
            # Standard mode
            if (self.metrics.signal_strength >= 85 and 
                self.metrics.market_tension > 75 and 
                self.metrics.signal_confidence > 80):
                self.metrics.current_signal = "FIRE!"
                self.metrics.signal_level = SignalLevel.FIRE
                
                if market_bias == "BUY":
                    self.buy_signals += 1
                else:
                    self.sell_signals += 1
                self.total_signals += 1
                
            elif self.metrics.signal_strength >= 75 and self.metrics.signal_confidence > 70:
                self.metrics.current_signal = "READY"
                self.metrics.signal_level = SignalLevel.READY
                
            elif self.metrics.signal_strength >= 60:
                self.metrics.current_signal = "WATCH"
                self.metrics.signal_level = SignalLevel.WATCH
                
            elif self.metrics.signal_strength >= 40:
                self.metrics.current_signal = "HOLD"
                self.metrics.signal_level = SignalLevel.HOLD
                
            else:
                self.metrics.current_signal = "WAIT"
                self.metrics.signal_level = SignalLevel.WAIT
    
    def _calculate_gold_momentum(self, market_data: pd.DataFrame):
        """Calculer le momentum or (comme MQL5)"""
        
        fast_ma = market_data['close'].rolling(self.fast_ma_period).mean()
        
        if len(fast_ma) >= 3:
            slope1 = fast_ma.iloc[-1] - fast_ma.iloc[-2]
            slope2 = fast_ma.iloc[-2] - fast_ma.iloc[-3]
            
            self.metrics.gold_momentum = (slope1 + slope2) * 1000
        
        # Bias strength
        rsi = self._calculate_rsi(market_data, self.rsi_period)
        if not np.isnan(rsi):
            self.metrics.gold_bias_strength = abs(rsi - 50) * 2
    
    def _update_precision_score(self):
        """Mettre à jour le score de précision (comme MQL5)"""
        
        market_vol = self._get_current_volatility()
        
        volatility_score = max(0, 100 - market_vol * 10)
        confidence_score = self.metrics.signal_confidence
        tension_score = max(0, 100 - self.metrics.market_tension)
        strength_score = self.metrics.signal_strength
        
        self.metrics.precision_score = (
            volatility_score * 0.25 + 
            confidence_score * 0.3 + 
            tension_score * 0.2 + 
            strength_score * 0.25
        )
    
    def _calculate_volatility(self, market_data: pd.DataFrame) -> float:
        """Calculer la volatilité (ATR simplifié)"""
        
        if len(market_data) < 20:
            return 0.3
        
        high_low = market_data['high'] - market_data['low']
        atr = high_low.rolling(14).mean().iloc[-1]
        
        current_price = market_data['close'].iloc[-1]
        normalized_vol = (atr / current_price) * 100 if current_price != 0 else 0
        
        return normalized_vol
    
    def _get_current_volatility(self) -> float:
        """Obtenir la volatilité actuelle"""
        # Simplifié - devrait être stocké
        return 0.5
    
    def _calculate_rsi(self, market_data: pd.DataFrame, period: int) -> float:
        """Calculer RSI"""
        
        if len(market_data) < period + 1:
            return np.nan
        
        delta = market_data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def _calculate_macd(self, market_data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Calculer MACD"""
        
        exp1 = market_data['close'].ewm(span=self.macd_fast, adjust=False).mean()
        exp2 = market_data['close'].ewm(span=self.macd_slow, adjust=False).mean()
        
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=self.macd_signal, adjust=False).mean()
        
        return macd_line, signal_line
    
    def _calculate_stochastic(self, market_data: pd.DataFrame) -> Tuple[float, float]:
        """Calculer Stochastic"""
        
        if len(market_data) < self.stoch_k:
            return np.nan, np.nan
        
        low_min = market_data['low'].rolling(self.stoch_k).min()
        high_max = market_data['high'].rolling(self.stoch_k).max()
        
        stoch_k = 100 * (market_data['close'] - low_min) / (high_max - low_min)
        stoch_d = stoch_k.rolling(self.stoch_d).mean()
        
        return stoch_k.iloc[-1], stoch_d.iloc[-1]
    
    def export_signal_for_hive(self) -> Dict:
        """Exporter le signal pour la Hive SWARNE"""
        
        return {
            'type': self.metrics.market_bias,
            'strength': self.metrics.signal_strength,
            'confidence': self.metrics.signal_confidence,
            'signal_level': self.metrics.signal_level.value,
            'signal_text': self.metrics.current_signal,
            'market_tension': self.metrics.market_tension,
            'precision_score': self.metrics.precision_score,
            'combat_readiness': self.metrics.combat_readiness,
            'gold_momentum': self.metrics.gold_momentum,
            'timestamp': datetime.now().isoformat()
        }


class GoldenEyes:
    """
    👁️ GOLDENEYES - Les Yeux d'Or
    
    Système de vision multi-temporelle pour détecter
    les moments clés sur toutes les échelles de temps.
    
    Comme un chef d'orchestre qui voit TOUT!
    """
    
    def __init__(self, symbol: str, mt5_connection):
        self.symbol = symbol
        self.mt5 = mt5_connection
        
        # Créer les yeux d'or pour chaque timeframe
        self.eyes: Dict[TimeFrame, GoldenEye] = {}
        
        self._initialize_eyes()
        
        # État global
        self.global_key_moment_detected = False
        self.dominant_timeframe = None
        self.master_signal = "NEUTRAL"
        self.master_strength = 0.0
        
        logger.info("👁️ GOLDENEYES initialized")
        logger.info(f"👁️ Watching {len(self.eyes)} timeframes")
    
    def _initialize_eyes(self):
        """Initialiser les yeux d'or avec importances"""
        
        # Configuration des importances par timeframe
        importances = {
            TimeFrame.SECOND: 0.05,      # Scalping ultra
            TimeFrame.MINUTE: 0.10,      # Scalping
            TimeFrame.FIVE_MIN: 0.15,    # Court terme
            TimeFrame.FIFTEEN_MIN: 0.12, # Court terme
            TimeFrame.HOUR: 0.18,        # Tendance
            TimeFrame.FOUR_HOUR: 0.15,   # Structure
            TimeFrame.DAY: 0.12,         # Structure
            TimeFrame.WEEK: 0.08,        # Cycle
            TimeFrame.MONTH: 0.03,       # Saison
            TimeFrame.YEAR: 0.02         # Macro
        }
        
        for tf, importance in importances.items():
            self.eyes[tf] = GoldenEye(
                timeframe=tf,
                importance=importance,
                last_key_moment=None,
                key_moments_detected=0
            )
        
        logger.info(f"👁️ {len(self.eyes)} Golden Eyes created")
    
    def scan_all_timeframes(self, market_data_dict: Dict[TimeFrame, pd.DataFrame]) -> Dict:
        """
        Scanner tous les timeframes pour détecter les moments clés
        
        Returns: Summary de la vision multi-temporelle
        """
        
        key_moments = []
        total_strength = 0.0
        weighted_signals = {"BUY": 0.0, "SELL": 0.0, "NEUTRAL": 0.0}
        
        for tf, eye in self.eyes.items():
            if not eye.is_active:
                continue
            
            # Obtenir les données pour ce timeframe
            market_data = market_data_dict.get(tf)
            
            if market_data is None or market_data.empty:
                continue
            
            # Analyser ce timeframe
            moment = self._analyze_timeframe(eye, market_data)
            
            if moment['is_key_moment']:
                key_moments.append(moment)
                eye.key_moments_detected += 1
                eye.last_key_moment = datetime.now()
            
            # Accumuler les signaux pondérés
            signal = moment['trend_direction']
            strength = moment['signal_strength']
            importance = eye.importance
            
            weighted_signals[signal] += strength * importance
            total_strength += strength * importance
        
        # Déterminer le signal dominant
        if total_strength > 0:
            self.master_signal = max(weighted_signals, key=weighted_signals.get)
            self.master_strength = weighted_signals[self.master_signal] / total_strength * 100
        else:
            self.master_signal = "NEUTRAL"
            self.master_strength = 0.0
        
        # Déterminer le timeframe dominant
        if key_moments:
            self.dominant_timeframe = max(
                key_moments,
                key=lambda m: m['importance'] * m['signal_strength']
            )['timeframe']
        
        # Détecter si moment clé global
        self.global_key_moment_detected = (
            len(key_moments) >= 3 and  # Au moins 3 timeframes alignés
            self.master_strength >= 70  # Signal fort
        )
        
        return {
            'global_key_moment': self.global_key_moment_detected,
            'master_signal': self.master_signal,
            'master_strength': self.master_strength,
            'dominant_timeframe': self.dominant_timeframe.value if self.dominant_timeframe else None,
            'key_moments_count': len(key_moments),
            'key_moments': key_moments,
            'all_timeframes': {
                tf.value: {
                    'signal': eye.trend_direction,
                    'strength': eye.signal_strength,
                    'momentum': eye.momentum,
                    'volatility': eye.volatility
                }
                for tf, eye in self.eyes.items()
            }
        }
    
    def _analyze_timeframe(self, eye: GoldenEye, market_data: pd.DataFrame) -> Dict:
        """Analyser un timeframe spécifique"""
        
        # Calculer les métriques pour ce timeframe
        trend = self._calculate_trend(market_data)
        momentum = self._calculate_momentum(market_data)
        volatility = self._calculate_volatility(market_data)
        
        # Détecter si c'est un moment clé
        is_key_moment = self._detect_key_moment(trend, momentum, volatility, eye.timeframe)
        
        # Calculer la force du signal
        signal_strength = abs(momentum) * (1 + trend['strength'] / 100)
        signal_strength = min(100, signal_strength)
        
        # Mettre à jour l'œil
        eye.trend_direction = trend['direction']
        eye.momentum = momentum
        eye.volatility = volatility
        eye.signal_strength = signal_strength
        
        return {
            'timeframe': eye.timeframe,
            'is_key_moment': is_key_moment,
            'trend_direction': trend['direction'],
            'trend_strength': trend['strength'],
            'momentum': momentum,
            'volatility': volatility,
            'signal_strength': signal_strength,
            'importance': eye.importance
        }
    
    def _calculate_trend(self, market_data: pd.DataFrame) -> Dict:
        """Calculer la tendance"""
        
        if len(market_data) < 20:
            return {'direction': 'NEUTRAL', 'strength': 0}
        
        # MA 20 vs MA 50
        ma_fast = market_data['close'].rolling(20).mean()
        ma_slow = market_data['close'].rolling(50).mean()
        
        if len(ma_fast) < 50:
            return {'direction': 'NEUTRAL', 'strength': 0}
        
        current_price = market_data['close'].iloc[-1]
        ma_fast_val = ma_fast.iloc[-1]
        ma_slow_val = ma_slow.iloc[-1]
        
        # Direction
        if ma_fast_val > ma_slow_val and current_price > ma_fast_val:
            direction = "BUY"
        elif ma_fast_val < ma_slow_val and current_price < ma_fast_val:
            direction = "SELL"
        else:
            direction = "NEUTRAL"
        
        # Strength
        if direction != "NEUTRAL":
            strength = abs((ma_fast_val - ma_slow_val) / ma_slow_val) * 1000
            strength = min(100, strength)
        else:
            strength = 0
        
        return {'direction': direction, 'strength': strength}
    
    def _calculate_momentum(self, market_data: pd.DataFrame) -> float:
        """Calculer le momentum"""
        
        if len(market_data) < 10:
            return 0.0
        
        # Rate of change sur 10 périodes
        roc = (market_data['close'].iloc[-1] - market_data['close'].iloc[-10]) / market_data['close'].iloc[-10]
        
        return roc * 100
    
    def _calculate_volatility(self, market_data: pd.DataFrame) -> float:
        """Calculer la volatilité"""
        
        if len(market_data) < 20:
            return 0.0
        
        returns = market_data['close'].pct_change()
        volatility = returns.rolling(20).std().iloc[-1] * 100
        
        return volatility
    
    def _detect_key_moment(self, trend: Dict, momentum: float, 
                          volatility: float, timeframe: TimeFrame) -> bool:
        """Détecter si c'est un moment clé pour ce timeframe"""
        
        # Seuils adaptatifs selon timeframe
        momentum_threshold = {
            TimeFrame.SECOND: 0.5,
            TimeFrame.MINUTE: 1.0,
            TimeFrame.FIVE_MIN: 1.5,
            TimeFrame.FIFTEEN_MIN: 2.0,
            TimeFrame.HOUR: 3.0,
            TimeFrame.FOUR_HOUR: 4.0,
            TimeFrame.DAY: 5.0,
            TimeFrame.WEEK: 7.0,
            TimeFrame.MONTH: 10.0,
            TimeFrame.YEAR: 15.0
        }
        
        threshold = momentum_threshold.get(timeframe, 2.0)
        
        # C'est un moment clé si:
        # 1. Momentum fort
        # 2. Trend fort
        # 3. Volatilité modérée (pas trop chaotique)
        
        is_key = (
            abs(momentum) >= threshold and
            trend['strength'] >= 50 and
            volatility < 10  # Pas trop volatile
        )
        
        return is_key
    
    def get_deployment_strategy(self) -> Dict:
        """
        Obtenir la stratégie de déploiement pour l'essaim
        
        Basé sur la vision multi-temporelle
        """
        
        if not self.global_key_moment_detected:
            return {
                'recommended_deployment': 'MINIMAL',
                'scouts': 2,
                'workers': 3,
                'guards': 0,
                'reason': 'Pas de moment clé global détecté'
            }
        
        # Moment clé global détecté !
        if self.master_strength >= 90:
            return {
                'recommended_deployment': 'MAXIMUM',
                'scouts': 8,
                'workers': 24,
                'guards': 8,
                'reason': f'MOMENT CLÉ ÉNORME ! {self.master_signal} @ {self.master_strength:.0f}%'
            }
        
        elif self.master_strength >= 80:
            return {
                'recommended_deployment': 'ELEVATED',
                'scouts': 4,
                'workers': 15,
                'guards': 4,
                'reason': f'Moment clé fort: {self.master_signal} @ {self.master_strength:.0f}%'
            }
        
        elif self.master_strength >= 70:
            return {
                'recommended_deployment': 'MODERATE',
                'scouts': 3,
                'workers': 10,
                'guards': 2,
                'reason': f'Moment clé modéré: {self.master_signal} @ {self.master_strength:.0f}%'
            }
        
        else:
            return {
                'recommended_deployment': 'CONSERVATIVE',
                'scouts': 2,
                'workers': 5,
                'guards': 0,
                'reason': f'Moment clé faible: {self.master_signal} @ {self.master_strength:.0f}%'
            }


class SniperScopeGoldenEyesIntegration:
    """
    🎯👁️ Intégration complète Sniper Scope + GoldenEyes
    
    Vision multi-temporelle avec précision de sniper !
    """
    
    def __init__(self, symbol: str, mt5_connection):
        self.symbol = symbol
        self.mt5 = mt5_connection
        
        # Composants
        self.sniper_scope = SniperScope(symbol, mt5_connection)
        self.golden_eyes = GoldenEyes(symbol, mt5_connection)
        
        # État
        self.last_update = datetime.now()
        self.update_interval = timedelta(seconds=1)  # Update chaque seconde
        
        logger.info("🎯👁️ SNIPER SCOPE + GOLDENEYES Integration ready!")
    
    def update(self, market_data: pd.DataFrame, 
               multi_tf_data: Dict[TimeFrame, pd.DataFrame] = None) -> Dict:
        """
        Mettre à jour le système complet
        
        Returns: Recommandation complète pour l'essaim
        """
        
        now = datetime.now()
        
        if now - self.last_update < self.update_interval:
            return self._get_last_recommendation()
        
        # 1. Update Sniper Scope (précision)
        sniper_metrics = self.sniper_scope.update(market_data)
        
        # 2. Scan GoldenEyes (vision multi-temporelle)
        if multi_tf_data is None:
            multi_tf_data = {TimeFrame.FIVE_MIN: market_data}
        
        golden_vision = self.golden_eyes.scan_all_timeframes(multi_tf_data)
        
        # 3. Combiner les deux systèmes
        recommendation = self._synthesize_recommendation(sniper_metrics, golden_vision)
        
        self.last_update = now
        self._last_recommendation = recommendation
        
        return recommendation
    
    def _synthesize_recommendation(self, sniper_metrics: SniperMetrics, 
                                   golden_vision: Dict) -> Dict:
        """Synthétiser la recommandation finale"""
        
        # Obtenir la stratégie de déploiement de GoldenEyes
        deployment = self.golden_eyes.get_deployment_strategy()
        
        # Ajuster selon Sniper Scope
        if sniper_metrics.signal_level.value >= SignalLevel.COMBAT_READY.value:
            # Sniper dit COMBAT READY → augmenter deployment
            deployment['scouts'] = min(deployment['scouts'] + 2, 8)
            deployment['workers'] = min(deployment['workers'] + 5, 24)
            deployment['guards'] = min(deployment['guards'] + 2, 8)
        
        # Signal final
        if golden_vision['master_signal'] != "NEUTRAL":
            final_signal = golden_vision['master_signal']
        else:
            final_signal = sniper_metrics.market_bias
        
        # Force finale (combinaison)
        final_strength = (
            golden_vision['master_strength'] * 0.6 +
            sniper_metrics.signal_strength * 0.4
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            
            # Signal final
            'signal': final_signal,
            'strength': final_strength,
            'precision': sniper_metrics.precision_score,
            'combat_readiness': sniper_metrics.combat_readiness,
            
            # Déploiement
            'deployment': deployment,
            
            # Vision multi-temporelle
            'golden_vision': {
                'global_key_moment': golden_vision['global_key_moment'],
                'dominant_timeframe': golden_vision['dominant_timeframe'],
                'key_moments_count': golden_vision['key_moments_count']
            },
            
            # Métriques Sniper
            'sniper': {
                'tension': sniper_metrics.market_tension,
                'confidence': sniper_metrics.signal_confidence,
                'signal_level': sniper_metrics.signal_level.name,
                'signal_text': sniper_metrics.current_signal
            },
            
            # Recommandation pour l'essaim
            'swarm_action': self._get_swarm_action(
                sniper_metrics, golden_vision, deployment
            )
        }
    
    def _get_swarm_action(self, sniper_metrics: SniperMetrics,
                         golden_vision: Dict, deployment: Dict) -> str:
        """Déterminer l'action pour l'essaim"""
        
        if golden_vision['global_key_moment'] and sniper_metrics.combat_readiness >= 95:
            return "🔥 DEPLOY ALL FORCES - MOMENT CLÉ MAJEUR !"
        
        elif golden_vision['global_key_moment']:
            return f"⚡ DEPLOY {deployment['recommended_deployment']} FORCES"
        
        elif sniper_metrics.signal_level == SignalLevel.FIRE_NOW:
            return "🎯 FIRE NOW - PRECISION STRIKE !"
        
        elif sniper_metrics.signal_level == SignalLevel.COMBAT_READY:
            return "⚔️ COMBAT READY - STANDBY FOR ACTION"
        
        elif sniper_metrics.signal_level.value >= SignalLevel.WATCH.value:
            return "👁️ WATCH CLOSE - SCOUTS ACTIVE"
        
        else:
            return "🛡️ HOLD POSITION - MINIMAL GUARD"
    
    def _get_last_recommendation(self) -> Dict:
        """Obtenir la dernière recommandation (cache)"""
        return getattr(self, '_last_recommendation', {})
    
    def export_for_swarne(self) -> Dict:
        """Exporter pour intégration SWARNE"""
        
        recommendation = self._get_last_recommendation()
        
        if not recommendation:
            return {
                'signal': 'NEUTRAL',
                'strength': 0,
                'deployment': {
                    'scouts': 2,
                    'workers': 5,
                    'guards': 0
                }
            }
        
        return {
            'signal': recommendation.get('signal', 'NEUTRAL'),
            'strength': recommendation.get('strength', 0),
            'precision': recommendation.get('precision', 0),
            'combat_readiness': recommendation.get('combat_readiness', 0),
            'deployment': recommendation.get('deployment', {}),
            'swarm_action': recommendation.get('swarm_action', ''),
            'golden_vision': recommendation.get('golden_vision', {})
        }


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    print("🎯👁️ SNIPER SCOPE + GOLDENEYES Test")
    print("="*60)
    
    # Créer données de test
    dates = pd.date_range(end=datetime.now(), periods=100, freq='1min')
    test_data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 4330,
        'high': np.random.randn(100).cumsum() + 4335,
        'low': np.random.randn(100).cumsum() + 4325,
        'close': np.random.randn(100).cumsum() + 4330,
        'volume': np.random.randint(100, 1000, 100)
    }, index=dates)
    
    # Test Sniper Scope
    print("\n🎯 Testing Sniper Scope...")
    sniper = SniperScope("XAUUSD", None)
    metrics = sniper.update(test_data)
    
    print(f"Signal: {metrics.current_signal}")
    print(f"Strength: {metrics.signal_strength:.1f}%")
    print(f"Confidence: {metrics.signal_confidence:.1f}%")
    print(f"Combat Readiness: {metrics.combat_readiness:.1f}%")
    print(f"Precision: {metrics.precision_score:.1f}")
    
    # Test GoldenEyes
    print("\n👁️ Testing GoldenEyes...")
    golden_eyes = GoldenEyes("XAUUSD", None)
    
    multi_tf_data = {
        TimeFrame.FIVE_MIN: test_data,
        TimeFrame.FIFTEEN_MIN: test_data,
        TimeFrame.HOUR: test_data
    }
    
    vision = golden_eyes.scan_all_timeframes(multi_tf_data)
    
    print(f"Global Key Moment: {vision['global_key_moment']}")
    print(f"Master Signal: {vision['master_signal']}")
    print(f"Master Strength: {vision['master_strength']:.1f}%")
    print(f"Dominant TF: {vision['dominant_timeframe']}")
    
    # Test Integration
    print("\n🎯👁️ Testing Full Integration...")
    integration = SniperScopeGoldenEyesIntegration("XAUUSD", None)
    recommendation = integration.update(test_data, multi_tf_data)
    
    print(f"Final Signal: {recommendation['signal']}")
    print(f"Final Strength: {recommendation['strength']:.1f}%")
    print(f"Swarm Action: {recommendation['swarm_action']}")
    print(f"Deployment: {recommendation['deployment']['recommended_deployment']}")
    print(f"  Scouts: {recommendation['deployment']['scouts']}")
    print(f"  Workers: {recommendation['deployment']['workers']}")
    print(f"  Guards: {recommendation['deployment']['guards']}")
    
    print("\n✅ Test completed!")
