

# ============================================================
# FIX UNICODE POUR WINDOWS - À ajouter au début du fichier
# ============================================================
import sys
import io
import logging

# Force UTF-8 encoding pour Windows
if sys.platform == 'win32':
    # Reconfigure stdout/stderr avec UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # Force UTF-8 pour le logging
    import locale
    if hasattr(locale, 'getpreferredencoding'):
        locale.getpreferredencoding = lambda: 'UTF-8'

# Configuration du logging avec UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║                    🐝 SWARNE! - THE HIVE 🐝                      ║
║                  Système d'Essaim de Trading                      ║
║                     Version 1.0 - ULTIMATE                        ║
╚══════════════════════════════════════════════════════════════════╝

Architecture:
    🐝 BEE (Abeille)      → Bot de trading individuel
    🏠 HIVE (Ruche)       → Coordinateur central
    🌸 FIELD (Champ)      → Interface avec MetaTrader
    🛡️ GUARDIAN (Gardien) → Risk Manager
"""

import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from collections import defaultdict, deque
import random
import time

# ==================== LOGGING CONFIGURATION ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('swarne_hive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SWARNE')

# ==================== ENUMS ====================

class BeeType(Enum):
    """Types d'abeilles dans la ruche"""
    SCOUT = "SCOUT"           # Exploration (stratégies risquées)
    WORKER = "WORKER"         # Production (stratégies éprouvées)
    GUARD = "GUARD"           # Protection (stop-loss strict)
    QUEEN = "QUEEN"           # Optimisation (meilleure stratégie)

class MarketCondition(Enum):
    """Conditions de marché"""
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"
    VOLATILE = "VOLATILE"
    CALM = "CALM"

class SignalStrength(Enum):
    """Force du signal"""
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4

# ==================== DATA CLASSES ====================

@dataclass
class BeeStrategy:
    """Stratégie d'une abeille"""
    ema_fast: int = 9
    ema_slow: int = 21
    adx_period: int = 14
    adx_threshold: float = 25.0
    rsi_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0
    atr_multiplier: float = 1.5
    risk_per_trade: float = 1.0
    
    def mutate(self, mutation_rate: float = 0.1) -> 'BeeStrategy':
        """Muter la stratégie"""
        if random.random() < mutation_rate:
            self.ema_fast = max(5, min(20, self.ema_fast + random.randint(-2, 2)))
        if random.random() < mutation_rate:
            self.ema_slow = max(15, min(50, self.ema_slow + random.randint(-5, 5)))
        if random.random() < mutation_rate:
            self.adx_threshold = max(15.0, min(40.0, self.adx_threshold + random.uniform(-5, 5)))
        return self

@dataclass
class Trade:
    """Représentation d'un trade"""
    bee_id: str
    symbol: str
    order_type: str  # 'BUY' or 'SELL'
    entry_price: float
    stop_loss: float
    take_profit: float
    volume: float
    entry_time: datetime
    ticket: int = 0
    exit_price: float = 0.0
    exit_time: Optional[datetime] = None
    pnl: float = 0.0
    status: str = "OPEN"  # OPEN, CLOSED, STOPPED
    
    def calculate_pnl(self, exit_price: float) -> float:
        """Calculer le PnL"""
        if self.order_type == 'BUY':
            return (exit_price - self.entry_price) * self.volume
        else:
            return (self.entry_price - exit_price) * self.volume

@dataclass
class BeePerformance:
    """Performance d'une abeille"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    fitness_score: float = 0.0

# ==================== 🐝 BEE CLASS ====================

class Bee:
    """
    Une abeille dans l'essaim.
    Chaque abeille a sa propre stratégie et peut trader de manière autonome.
    """
    
    def __init__(self, bee_id: str, bee_type: BeeType, strategy: Optional[BeeStrategy] = None):
        self.bee_id = bee_id
        self.bee_type = bee_type
        self.strategy = strategy if strategy else BeeStrategy()
        self.performance = BeePerformance()
        self.active = True
        self.current_trades: List[Trade] = []
        self.trade_history: List[Trade] = []
        self.birth_time = datetime.now()
        self.age = 0  # En secondes
        
        logger.info(f"🐝 {self.bee_id} né(e) ! Type: {bee_type.value}")
    
    def analyze_market(self, market_data: pd.DataFrame) -> Tuple[str, float]:
        """
        Analyser le marché et retourner un signal
        
        Returns:
            (signal, confidence) où signal = 'BUY', 'SELL', 'HOLD'
            confidence = 0.0 à 1.0
        """
        if len(market_data) < max(self.strategy.ema_slow, self.strategy.adx_period):
            return 'HOLD', 0.0
        
        # Calculer les indicateurs
        close = market_data['close'].values
        
        # EMA
        ema_fast = self._calculate_ema(close, self.strategy.ema_fast)
        ema_slow = self._calculate_ema(close, self.strategy.ema_slow)
        
        # ADX (simplifié)
        adx = self._calculate_adx(market_data, self.strategy.adx_period)
        
        # RSI
        rsi = self._calculate_rsi(close, self.strategy.rsi_period)
        
        # Analyse
        signal = 'HOLD'
        confidence = 0.0
        
        # Croisement EMA
        if ema_fast[-1] > ema_slow[-1] and ema_fast[-2] <= ema_slow[-2]:
            if adx > self.strategy.adx_threshold:
                signal = 'BUY'
                confidence = min(1.0, adx / 50.0)
        
        elif ema_fast[-1] < ema_slow[-1] and ema_fast[-2] >= ema_slow[-2]:
            if adx > self.strategy.adx_threshold:
                signal = 'SELL'
                confidence = min(1.0, adx / 50.0)
        
        # Ajustement avec RSI
        if signal == 'BUY' and rsi > self.strategy.rsi_overbought:
            confidence *= 0.5
        elif signal == 'SELL' and rsi < self.strategy.rsi_oversold:
            confidence *= 0.5
        
        return signal, confidence
    
    def _calculate_ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculer EMA"""
        ema = np.zeros_like(data)
        ema[0] = data[0]
        alpha = 2.0 / (period + 1.0)
        
        for i in range(1, len(data)):
            ema[i] = alpha * data[i] + (1 - alpha) * ema[i-1]
        
        return ema
    
    def _calculate_rsi(self, data: np.ndarray, period: int) -> float:
        """Calculer RSI"""
        if len(data) < period + 1:
            return 50.0
        
        deltas = np.diff(data[-period-1:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_adx(self, data: pd.DataFrame, period: int) -> float:
        """Calculer ADX (simplifié)"""
        if len(data) < period:
            return 0.0
        
        high = data['high'].values[-period:]
        low = data['low'].values[-period:]
        close = data['close'].values[-period:]
        
        # True Range
        tr = np.maximum(high - low, 
                       np.maximum(np.abs(high - np.roll(close, 1)), 
                                 np.abs(low - np.roll(close, 1))))
        
        atr = np.mean(tr)
        
        if atr == 0:
            return 0.0
        
        # Directional Movement
        up_move = high - np.roll(high, 1)
        down_move = np.roll(low, 1) - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        plus_di = 100 * np.mean(plus_dm) / atr
        minus_di = 100 * np.mean(minus_dm) / atr
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 0.0001)
        
        return dx
    
    def update_performance(self):
        """Mettre à jour les statistiques de performance"""
        if len(self.trade_history) == 0:
            return
        
        self.performance.total_trades = len(self.trade_history)
        
        winning = [t for t in self.trade_history if t.pnl > 0]
        losing = [t for t in self.trade_history if t.pnl <= 0]
        
        self.performance.winning_trades = len(winning)
        self.performance.losing_trades = len(losing)
        self.performance.total_pnl = sum(t.pnl for t in self.trade_history)
        
        if self.performance.total_trades > 0:
            self.performance.win_rate = self.performance.winning_trades / self.performance.total_trades
        
        if len(winning) > 0:
            self.performance.avg_win = sum(t.pnl for t in winning) / len(winning)
        
        if len(losing) > 0:
            self.performance.avg_loss = sum(t.pnl for t in losing) / len(losing)
        
        # Fitness score
        self.performance.fitness_score = self._calculate_fitness()
    
    def _calculate_fitness(self) -> float:
        """
        Calculer le score de fitness de l'abeille
        Plus le score est élevé, meilleure est l'abeille
        """
        if self.performance.total_trades < 5:
            return 0.0
        
        fitness = 0.0
        
        # Win rate (30%)
        fitness += self.performance.win_rate * 0.3
        
        # Total PnL normalisé (40%)
        pnl_score = min(1.0, max(0.0, (self.performance.total_pnl / 1000.0) + 0.5))
        fitness += pnl_score * 0.4
        
        # Ratio Gain/Perte (30%)
        if self.performance.avg_loss != 0:
            profit_factor = abs(self.performance.avg_win / self.performance.avg_loss)
            ratio_score = min(1.0, profit_factor / 3.0)
            fitness += ratio_score * 0.3
        
        return fitness

# ==================== 🛡️ GUARDIAN (RISK MANAGER) ====================

class Guardian:
    """
    Le Gardien de la Ruche - Risk Manager
    Protège le capital et valide chaque trade
    """
    
    def __init__(self, initial_capital: float = 10000.0, max_daily_loss_pct: float = 3.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_daily_loss_pct = max_daily_loss_pct
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.total_trades = 0
        self.trading_allowed = True
        
        logger.info(f"🛡️ Guardian initialized with capital: ${initial_capital:,.2f}")
    
    def validate_trade(self, bee: Bee, signal: str, confidence: float, 
                      current_price: float, atr: float) -> Tuple[bool, float, float, float]:
        """
        Valider un trade proposé par une abeille
        
        Returns:
            (approved, volume, stop_loss, take_profit)
        """
        # Vérifier la limite journalière
        if not self._check_daily_limit():
            return False, 0.0, 0.0, 0.0
        
        # Vérifier la confiance minimum
        if confidence < 0.5:
            return False, 0.0, 0.0, 0.0
        
        # Calculer la taille de position
        risk_amount = self.current_capital * (bee.strategy.risk_per_trade / 100)
        
        # Stop loss basé sur ATR
        if signal == 'BUY':
            stop_loss = current_price - atr * bee.strategy.atr_multiplier
            take_profit = current_price + atr * bee.strategy.atr_multiplier * 2.0
        else:
            stop_loss = current_price + atr * bee.strategy.atr_multiplier
            take_profit = current_price - atr * bee.strategy.atr_multiplier * 2.0
        
        # Calculer le volume
        risk_per_unit = abs(current_price - stop_loss)
        if risk_per_unit == 0:
            return False, 0.0, 0.0, 0.0
        
        volume = risk_amount / risk_per_unit
        volume = max(0.01, min(volume, 10.0))  # Limites de volume
        
        # Ajuster selon la confiance
        volume *= confidence
        
        logger.info(f"✅ Guardian approves: {signal} volume={volume:.2f}, SL={stop_loss:.5f}, TP={take_profit:.5f}")
        
        return True, volume, stop_loss, take_profit
    
    def _check_daily_limit(self) -> bool:
        """Vérifier si la limite de perte journalière est atteinte"""
        daily_loss_pct = abs(self.daily_pnl / self.initial_capital) * 100
        
        if daily_loss_pct >= self.max_daily_loss_pct:
            self.trading_allowed = False
            logger.warning(f"⛔ Daily loss limit reached: {daily_loss_pct:.2f}%")
            return False
        
        return True
    
    def update_capital(self, pnl: float):
        """Mettre à jour le capital"""
        self.current_capital += pnl
        self.daily_pnl += pnl
        self.total_trades += 1
        self.daily_trades += 1
    
    def reset_daily(self):
        """Réinitialiser les compteurs journaliers"""
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.trading_allowed = True
        logger.info("🔄 Daily reset complete")

# ==================== 🌸 FIELD (METATRADER INTERFACE) ====================

class Field:
    """
    Le Champ - Interface avec MetaTrader 5
    Gère toutes les interactions avec le broker
    """
    
    def __init__(self, symbol: str = "EURUSD"):
        self.symbol = symbol
        self.connected = False
        self.account_info = {}
        
        # Initialiser MT5
        if not mt5.initialize():
            logger.error("❌ Failed to initialize MetaTrader 5")
            raise ConnectionError("Cannot connect to MetaTrader 5")
        
        self.connected = True
        self._update_account_info()
        logger.info(f"🌸 Field connected to MetaTrader 5 - Symbol: {symbol}")
    
    def _update_account_info(self):
        """Mettre à jour les informations du compte"""
        account = mt5.account_info()
        if account:
            self.account_info = {
                'balance': account.balance,
                'equity': account.equity,
                'margin': account.margin,
                'free_margin': account.margin_free,
                'leverage': account.leverage
            }
    
    def get_market_data(self, timeframe: int = mt5.TIMEFRAME_M15, bars: int = 100) -> pd.DataFrame:
        """Récupérer les données de marché"""
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, bars)
        
        if rates is None or len(rates) == 0:
            logger.error(f"❌ Failed to get market data for {self.symbol}")
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        return df
    
    def calculate_atr(self, timeframe: int = mt5.TIMEFRAME_M15, period: int = 14) -> float:
        """Calculer l'ATR"""
        data = self.get_market_data(timeframe, period + 10)
        
        if len(data) < period:
            return 0.0001  # Valeur par défaut
        
        high = data['high'].values
        low = data['low'].values
        close = data['close'].values
        
        tr = np.maximum(high - low, 
                       np.maximum(np.abs(high - np.roll(close, 1)), 
                                 np.abs(low - np.roll(close, 1))))
        
        atr = np.mean(tr[-period:])
        
        return atr
    
    def place_order(self, order_type: str, volume: float, 
                   stop_loss: float = 0, take_profit: float = 0) -> Optional[int]:
        """
        Placer un ordre sur MetaTrader
        
        Returns:
            ticket number or None if failed
        """
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"❌ Symbol {self.symbol} not found")
            return None
        
        if not symbol_info.visible:
            if not mt5.symbol_select(self.symbol, True):
                logger.error(f"❌ Failed to select symbol {self.symbol}")
                return None
        
        # Préparer la requête
        price = mt5.symbol_info_tick(self.symbol).ask if order_type == 'BUY' else mt5.symbol_info_tick(self.symbol).bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": float(volume),
            "type": mt5.ORDER_TYPE_BUY if order_type == 'BUY' else mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": float(stop_loss) if stop_loss > 0 else 0,
            "tp": float(take_profit) if take_profit > 0 else 0,
            "deviation": 20,
            "magic": 123456,
            "comment": "SWARNE!",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"❌ Order failed: {result.comment}")
            return None
        
        logger.info(f"✅ Order placed: {order_type} {volume} @ {price:.5f} - Ticket: {result.order}")
        return result.order
    
    def close_position(self, ticket: int) -> bool:
        """Fermer une position"""
        positions = mt5.positions_get(ticket=ticket)
        
        if positions is None or len(positions) == 0:
            logger.warning(f"⚠️ Position {ticket} not found")
            return False
        
        position = positions[0]
        
        order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(self.symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(self.symbol).ask
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": position.volume,
            "type": order_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": "SWARNE! Close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"❌ Failed to close position {ticket}: {result.comment}")
            return False
        
        logger.info(f"✅ Position {ticket} closed successfully")
        return True
    
    def get_current_price(self) -> float:
        """Obtenir le prix actuel"""
        tick = mt5.symbol_info_tick(self.symbol)
        if tick:
            return (tick.ask + tick.bid) / 2
        return 0.0
    
    def get_market_info(self):
        """
        Récupère les informations du marché pour le générateur de signaux
        
        Returns:
            dict: Informations de marché (price, atr, spread, trend, volatility)
        """
        try:
            # Prix actuel
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                return None
            
            price = tick.bid
            spread = (tick.ask - tick.bid) / tick.bid if tick.bid > 0 else 0
            
            # Récupérer barres pour ATR
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M5, 0, 20)
            if rates is None or len(rates) < 14:
                return {
                    'price': price,
                    'atr': 0,
                    'spread': spread,
                    'trend': 'NEUTRAL',
                    'volatility': 0
                }
            
            # Calculer ATR
            highs = np.array([r['high'] for r in rates])
            lows = np.array([r['low'] for r in rates])
            closes = np.array([r['close'] for r in rates])
            
            tr1 = highs[1:] - lows[1:]
            tr2 = np.abs(highs[1:] - closes[:-1])
            tr3 = np.abs(lows[1:] - closes[:-1])
            
            tr = np.maximum(tr1, np.maximum(tr2, tr3))
            atr = np.mean(tr[-14:]) if len(tr) >= 14 else np.mean(tr)
            
            volatility = (atr / price * 100) if price > 0 else 0
            
            # Tendance simple
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
            
        except Exception as e:
            logger.error(f"Error in get_market_info: {e}")
            return None
    
    def shutdown(self):
        """Fermer la connexion MT5"""
        mt5.shutdown()
        self.connected = False
        logger.info("🌸 Field disconnected from MetaTrader 5")

# ==================== 🏠 HIVE (COORDINATEUR CENTRAL) ====================

class Hive:
    """
    La Ruche - Coordinateur central de l'essaim
    Gère toutes les abeilles et coordonne leurs actions
    """
    
    def __init__(self, initial_capital: float = 10000.0, num_bees: int = 20, symbol: str = "EURUSD"):
        self.guardian = Guardian(initial_capital)
        self.field = Field(symbol)
        self.bees: List[Bee] = []
        self.generation = 0
        self.best_bee: Optional[Bee] = None
        
        # Créer l'essaim initial
        self._create_initial_swarm(num_bees)
        
        logger.info(f"🏠 Hive initialized with {num_bees} bees")
    
    def _create_initial_swarm(self, num_bees: int):
        """Créer l'essaim initial"""
        # Répartition des types d'abeilles
        num_scouts = num_bees // 4
        num_workers = num_bees // 2
        num_guards = num_bees // 4
        
        bee_id = 0
        
        # Scouts (exploration)
        for i in range(num_scouts):
            strategy = BeeStrategy(
                ema_fast=random.randint(5, 15),
                ema_slow=random.randint(15, 40),
                adx_threshold=random.uniform(20, 35)
            )
            self.bees.append(Bee(f"SCOUT_{bee_id}", BeeType.SCOUT, strategy))
            bee_id += 1
        
        # Workers (production)
        for i in range(num_workers):
            strategy = BeeStrategy()  # Stratégie par défaut
            self.bees.append(Bee(f"WORKER_{bee_id}", BeeType.WORKER, strategy))
            bee_id += 1
        
        # Guards (protection)
        for i in range(num_guards):
            strategy = BeeStrategy(atr_multiplier=2.0, risk_per_trade=0.5)
            self.bees.append(Bee(f"GUARD_{bee_id}", BeeType.GUARD, strategy))
            bee_id += 1
        
        # CORRECTION: Donner field à toutes les abeilles
        for bee in self.bees:
            bee.field = self.field
    
    def run_cycle(self):
        """Exécuter un cycle de trading pour tout l'essaim"""
        logger.info(f"\n{'='*60}")
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
        
        # Faire travailler chaque abeille
        for bee in self.bees:
            if not bee.active:
                continue
            
            # Analyser le marché
            signal, confidence = bee.analyze_market(market_data)
            
            if signal in ['BUY', 'SELL'] and confidence > 0.5:
                logger.info(f"🐝 {bee.bee_id} → Signal: {signal} | Confidence: {confidence:.2%}")
                
                # Valider avec le Guardian
                approved, volume, stop_loss, take_profit = self.guardian.validate_trade(
                    bee, signal, confidence, current_price, atr
                )
                
                if approved:
                    # Placer l'ordre
                    ticket = self.field.place_order(signal, volume, stop_loss, take_profit)
                    
                    if ticket:
                        # Enregistrer le trade
                        trade = Trade(
                            bee_id=bee.bee_id,
                            symbol=self.field.symbol,
                            order_type=signal,
                            entry_price=current_price,
                            stop_loss=stop_loss,
                            take_profit=take_profit,
                            volume=volume,
                            entry_time=datetime.now(),
                            ticket=ticket
                        )
                        
                        bee.current_trades.append(trade)
                        logger.info(f"✅ {bee.bee_id} placed {signal} order - Ticket: {ticket}")
        
        # Mettre à jour les positions ouvertes
        self._update_open_positions()
        
        # Évolution de l'essaim
        if self.generation % 10 == 0 and self.generation > 0:
            self._evolve_swarm()
        
        self.generation += 1
        time.sleep(1)
    
    def _update_open_positions(self):
        """Mettre à jour toutes les positions ouvertes"""
        for bee in self.bees:
            for trade in bee.current_trades[:]:
                # Vérifier si la position est toujours ouverte
                positions = mt5.positions_get(ticket=trade.ticket)
                
                if positions is None or len(positions) == 0:
                    # Position fermée
                    current_price = self.field.get_current_price()
                    pnl = trade.calculate_pnl(current_price)
                    
                    trade.exit_price = current_price
                    trade.exit_time = datetime.now()
                    trade.pnl = pnl
                    trade.status = "CLOSED"
                    
                    # Mettre à jour les statistiques
                    bee.current_trades.remove(trade)
                    bee.trade_history.append(trade)
                    bee.update_performance()
                    self.guardian.update_capital(pnl)
                    
                    logger.info(f"💰 {bee.bee_id} - Trade closed: PnL = ${pnl:.2f}")
    
    def _evolve_swarm(self):
        """Faire évoluer l'essaim (sélection naturelle)"""
        logger.info(f"\n🧬 EVOLUTION - Generation {self.generation}")
        
        # Calculer les performances
        for bee in self.bees:
            bee.update_performance()
        
        # Trier par fitness
        self.bees.sort(key=lambda b: b.performance.fitness_score, reverse=True)
        
        # Identifier la meilleure abeille
        if self.bees[0].performance.fitness_score > 0:
            self.best_bee = self.bees[0]
            logger.info(f"👑 QUEEN BEE: {self.best_bee.bee_id} - Fitness: {self.best_bee.performance.fitness_score:.3f}")
        
        # CORRECTION: Garder au moins 50% des abeilles (pas 25%)
        # Et seulement si elles ont une fitness très négative
        cutoff = len(self.bees) // 2  # Garder top 50%
        weak_bees = [bee for bee in self.bees[cutoff:] if bee.performance.fitness_score < -0.5]
        
        for bee in weak_bees:
            logger.info(f"💀 {bee.bee_id} eliminated (Fitness: {bee.performance.fitness_score:.3f})")
        
        # Retirer seulement les vraiment faibles
        for bee in weak_bees:
            if bee in self.bees:
                self.bees.remove(bee)
        
        # Reproduire les meilleures
        num_new_bees = len(weak_bees)
        for i in range(num_new_bees):
            # Sélectionner deux parents
            parent1 = random.choice(self.bees[:len(self.bees)//2])
            parent2 = random.choice(self.bees[:len(self.bees)//2])
            
            # Créer un enfant (crossover)
            child_strategy = BeeStrategy(
                ema_fast=(parent1.strategy.ema_fast + parent2.strategy.ema_fast) // 2,
                ema_slow=(parent1.strategy.ema_slow + parent2.strategy.ema_slow) // 2,
                adx_threshold=(parent1.strategy.adx_threshold + parent2.strategy.adx_threshold) / 2
            )
            
            # Mutation
            child_strategy.mutate()
            
            # Créer la nouvelle abeille
            child_id = f"GEN{self.generation}_{i}"
            child_type = random.choice([BeeType.SCOUT, BeeType.WORKER, BeeType.GUARD])
            child = Bee(child_id, child_type, child_strategy)
            
            # CORRECTION: Donner field à la nouvelle abeille
            child.field = self.field
            
            self.bees.append(child)
            logger.info(f"🐣 New bee born: {child_id}")
    
    def get_statistics(self) -> Dict:
        """Obtenir les statistiques de la ruche"""
        active_bees = [b for b in self.bees if b.active]
        total_trades = sum(b.performance.total_trades for b in active_bees)
        avg_fitness = np.mean([b.performance.fitness_score for b in active_bees]) if active_bees else 0
        
        return {
            'generation': self.generation,
            'active_bees': len(active_bees),
            'total_trades': total_trades,
            'capital': self.guardian.current_capital,
            'daily_pnl': self.guardian.daily_pnl,
            'avg_fitness': avg_fitness,
            'best_bee': self.best_bee.bee_id if self.best_bee else "None"
        }
    
    def print_statistics(self):
        """Afficher les statistiques"""
        stats = self.get_statistics()
        
        print(f"\n{'='*60}")
        print(f"📊 SWARNE! STATISTICS - Generation {stats['generation']}")
        print(f"{'='*60}")
        print(f"🐝 Active Bees: {stats['active_bees']}")
        print(f"📈 Total Trades: {stats['total_trades']}")
        print(f"💰 Capital: ${stats['capital']:,.2f}")
        print(f"📊 Daily P&L: ${stats['daily_pnl']:+,.2f}")
        print(f"🎯 Avg Fitness: {stats['avg_fitness']:.3f}")
        print(f"👑 Best Bee: {stats['best_bee']}")
        print(f"{'='*60}\n")
    
    def shutdown(self):
        """Arrêter la ruche"""
        logger.info("🏠 Shutting down Hive...")
        
        # Fermer toutes les positions
        for bee in self.bees:
            for trade in bee.current_trades:
                self.field.close_position(trade.ticket)
        
        self.field.shutdown()
        logger.info("✅ Hive shutdown complete")

# ==================== 🚀 MAIN ====================

def main():
    """Fonction principale"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    🐝 SWARNE! - THE HIVE 🐝                      ║
║                  Système d'Essaim de Trading                      ║
║                     Version 1.0 - ULTIMATE                        ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Configuration
    INITIAL_CAPITAL = 10000.0
    NUM_BEES = 20
    SYMBOL = "EURUSD"
    MAX_CYCLES = 100
    
    # Créer la ruche
    hive = Hive(INITIAL_CAPITAL, NUM_BEES, SYMBOL)
    
    try:
        # Boucle principale
        for cycle in range(MAX_CYCLES):
            hive.run_cycle()
            
            # Afficher les stats toutes les 10 itérations
            if cycle % 10 == 0:
                hive.print_statistics()
            
            # Attendre entre les cycles
            time.sleep(60)  # 1 minute entre chaque cycle
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    
    finally:
        hive.shutdown()
        print("\n✅ SWARNE! terminated successfully")

if __name__ == "__main__":
    main()
