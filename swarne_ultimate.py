

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

# 🎯👁️ Sniper Scope + GoldenEyes Integration
try:
    from sniper_scope_goldeneyes import (
        SniperScopeGoldenEyesIntegration,
        TimeFrame
    )
    SNIPER_GOLDEN_AVAILABLE = True
except ImportError:
    SNIPER_GOLDEN_AVAILABLE = False
    logger.warning("⚠️ Sniper Scope + GoldenEyes not available")
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
    
    @property
    def capital(self):
        """Alias pour current_capital (compatibilité dashboard)"""
        return self.current_capital
    
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
        Récupère les informations du marché pour bee_signal_generator
        
        Returns:
            dict avec price, atr, spread, trend, volatility, close_prices
        """
        try:
            # Prix actuel
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                return None
            
            price = tick.bid
            spread = (tick.ask - tick.bid) / tick.bid if tick.bid > 0 else 0
            
            # Récupérer données historiques
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M15, 0, 100)
            if rates is None or len(rates) < 20:
                return {
                    'price': price,
                    'atr': 0.001,
                    'spread': spread,
                    'trend': 'NEUTRAL',
                    'volatility': 0.01,
                    'close_prices': []
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
            
            volatility = (atr / price * 100) if price > 0 else 0.01
            
            # Tendance simple
            if len(closes) >= 20:
                ma_fast = np.mean(closes[-10:])
                ma_slow = np.mean(closes[-20:])
                
                if ma_fast > ma_slow * 1.002:
                    trend = 'BULLISH'
                elif ma_fast < ma_slow * 0.998:
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
                'volatility': volatility,
                'close_prices': closes.tolist()  # Pour bee_signal_generator
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
        self.trade_history: List[Trade] = []  # CORRECTION: Historique des trades pour le dashboard
        
        # 🎯👁️ Sniper Scope + GoldenEyes Integration
        if SNIPER_GOLDEN_AVAILABLE:
            self.sniper_golden = SniperScopeGoldenEyesIntegration(
                symbol=symbol,
                mt5_connection=mt5
            )
            logger.info("🎯👁️ Sniper Scope + GoldenEyes INTEGRATED!")
        else:
            self.sniper_golden = None
            logger.warning("⚠️ Sniper Scope + GoldenEyes NOT available - running without multi-timeframe vision")
        
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
        
        # CORRECTION: Donner field à toutes les abeilles dès la création
        for bee in self.bees:
            bee.field = self.field
    
    def run_cycle(self):
        """Exécuter un cycle de trading avec déploiement par RÔLES (SCOUTS → WORKERS → GUARDS)"""
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
        
        # ════════════════════════════════════════════════════════════
        # 🎯👁️ SNIPER SCOPE + GOLDENEYES VISION
        # ════════════════════════════════════════════════════════════
        
        recommendation = None
        if self.sniper_golden is not None:
            # Préparer données multi-timeframe
            multi_tf_data = {
                TimeFrame.FIVE_MIN: market_data,
                # D'autres timeframes peuvent être ajoutés ici
            }
            
            # Obtenir la recommandation complète
            recommendation = self.sniper_golden.update(market_data, multi_tf_data)
            
            # Log la vision
            logger.info("")
            logger.info("🎯👁️ SNIPER SCOPE + GOLDENEYES VISION:")
            logger.info(f"  Signal: {recommendation['signal']} @ {recommendation['strength']:.1f}%")
            logger.info(f"  Precision: {recommendation['precision']:.1f}")
            logger.info(f"  Combat Readiness: {recommendation['combat_readiness']:.1f}%")
            logger.info(f"  Swarm Action: {recommendation['swarm_action']}")
            
            if recommendation['golden_vision']['global_key_moment']:
                logger.info("  👁️ GLOBAL KEY MOMENT DETECTED!")
                logger.info(f"  Dominant TF: {recommendation['golden_vision']['dominant_timeframe']}")
                logger.info(f"  Key Moments: {recommendation['golden_vision']['key_moments_count']}")
            
            deployment = recommendation['deployment']
            logger.info(f"\n🐝 Recommended Deployment: {deployment['recommended_deployment']}")
            logger.info(f"  Reason: {deployment['reason']}")
            logger.info(f"  Scouts: {deployment['scouts']}")
            logger.info(f"  Workers: {deployment['workers']}")
            logger.info(f"  Guards: {deployment['guards']}")
        
        # Calculer la volatilité du marché (pour modes adaptatifs)
        market_volatility = self._calculate_market_volatility()
        is_warrior_mode = market_volatility > 0.5
        mode_name = "⚔️ GUERRIER" if is_warrior_mode else "🌾 RÉCOLTE"
        
        # Compter les positions ouvertes actuelles
        total_open_positions = sum(len(bee.current_trades) for bee in self.bees)
        logger.info(f"📊 Mode: {mode_name} | Volatilité: {market_volatility:.2f} | Positions: {total_open_positions}")
        
        # ═══════════════════════════════════════════════════════════
        # DÉPLOIEMENT PAR RÔLES (GUIDÉ PAR SNIPER SCOPE + GOLDENEYES)
        # ═══════════════════════════════════════════════════════════
        
        # Utiliser le signal de Sniper Scope + GoldenEyes si disponible
        master_signal = recommendation['signal'] if recommendation else 'NEUTRAL'
        master_confidence = recommendation['strength'] / 100.0 if recommendation else 0.5
        target_scouts = recommendation['deployment']['scouts'] if recommendation else 2
        target_workers = recommendation['deployment']['workers'] if recommendation else 3
        target_guards = recommendation['deployment']['guards'] if recommendation else 0
        
        # 🔥 ACTIVER LES ABEILLES SELON LA RECOMMANDATION
        logger.info(f"🔄 Adjusting swarm: {target_scouts} scouts, {target_workers} workers, {target_guards} guards")
        self._activate_bees_by_type('SCOUT', target_scouts)
        self._activate_bees_by_type('WORKER', target_workers)
        self._activate_bees_by_type('GUARD', target_guards)
        
        # Maintenant filtrer les abeilles actives par rôle
        scouts = [bee for bee in self.bees if bee.bee_type == 'SCOUT' and bee.active]
        workers = [bee for bee in self.bees if bee.bee_type == 'WORKER' and bee.active]
        guards = [bee for bee in self.bees if bee.bee_type == 'GUARD' and bee.active]
        
        logger.info(f"🐝 Essaim actif: {len(scouts)} scouts, {len(workers)} workers, {len(guards)} guards")
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 1: SCOUTS EXPLORENT (Nombre adaptatif)
        # ═══════════════════════════════════════════════════════════
        
        scout_signals = []
        
        for scout in scouts[:target_scouts]:
            if len(scout.current_trades) > 0:
                continue  # Skip si déjà en trade
            
            # Utiliser le signal master si disponible, sinon générer
            if master_signal in ['BUY', 'SELL']:
                signal = master_signal
                confidence = master_confidence
            else:
                # Générer le signal localement
                signal = 'HOLD'
                confidence = 0.0
                
                try:
                    if hasattr(scout, 'generate_signal'):
                        signal_data = scout.generate_signal()
                        if signal_data and isinstance(signal_data, dict):
                            signal = signal_data.get('type', 'HOLD')
                            raw_confidence = signal_data.get('confidence', 0)
                            confidence = raw_confidence / 100.0 if raw_confidence > 1.0 else raw_confidence
                    else:
                        signal, confidence = scout.analyze_market(market_data)
                except Exception as e:
                    logger.error(f"Error scout {scout.bee_id}: {e}")
                    continue
            
            if signal in ['BUY', 'SELL'] and confidence > 0.5:
                scout_signals.append({'type': signal, 'confidence': confidence})
                
                # Valider avec le Guardian
                approved, volume, stop_loss, take_profit = self.guardian.validate_trade(
                    scout, signal, confidence, current_price, atr
                )
                
                if approved:
                    # SCOUTS: lots réduits (exploration)
                    scout_volume = volume * 0.5
                    
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
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 2: WORKERS BUTINENT (SI SCOUTS CONFIRMENT OU MASTER SIGNAL)
        # ═══════════════════════════════════════════════════════════
        
        scout_confirmed = False
        dominant_signal = master_signal  # Utiliser le signal master par défaut
        avg_confidence = master_confidence
        
        if scout_signals:
            avg_confidence = sum(s['confidence'] for s in scout_signals) / len(scout_signals)
            scout_confirmed = avg_confidence >= 0.65  # 65% de confiance minimum
            
            if scout_confirmed:
                # Déterminer le signal dominant des scouts
                buy_count = sum(1 for s in scout_signals if s['type'] == 'BUY')
                sell_count = sum(1 for s in scout_signals if s['type'] == 'SELL')
                dominant_signal = 'BUY' if buy_count > sell_count else 'SELL'
                
                logger.info(f"🔍 SCOUTS CONFIRMED! {dominant_signal} @ {avg_confidence:.0%} - Sending WORKERS")
        elif master_signal in ['BUY', 'SELL'] and master_confidence >= 0.65:
            # Pas de scouts, mais signal master fort
            scout_confirmed = True
            logger.info(f"🎯 MASTER SIGNAL! {master_signal} @ {master_confidence:.0%} - Sending WORKERS")
        
        if scout_confirmed and dominant_signal in ['BUY', 'SELL']:
            for worker in workers[:target_workers]:
                if len(worker.current_trades) > 0:
                    continue  # Skip si déjà en trade
                
                # Utiliser le signal dominant
                signal = dominant_signal
                confidence = avg_confidence
                
                if confidence > 0.5:
                    # Valider avec le Guardian
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
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 3: GUARDS ATTAQUENT (MOMENT CLÉ GLOBAL OU MOMENTUM ÉNORME)
        # ═══════════════════════════════════════════════════════════
        
        guards_should_attack = False
        
        # Condition 1: Moment clé global détecté par GoldenEyes
        if recommendation and recommendation['golden_vision']['global_key_moment']:
            if recommendation['combat_readiness'] >= 95:
                guards_should_attack = True
                logger.info(f"⚔️ GLOBAL KEY MOMENT + COMBAT READY! - GUARDS ATTACK!")
            elif recommendation['combat_readiness'] >= 85 and target_guards > 0:
                guards_should_attack = True
                logger.info(f"⚔️ GLOBAL KEY MOMENT DETECTED! - GUARDS ATTACK!")
        
        # Condition 2: Momentum énorme (fallback si pas de GoldenEyes)
        elif scout_confirmed and avg_confidence >= 0.85:
            guards_should_attack = True
            logger.info(f"⚔️ MOMENTUM ÉNORME! Conf: {avg_confidence:.0%} - GUARDS ATTACK!")
        
        # Condition 3: Volatilité extrême + bon signal
        elif scout_confirmed and is_warrior_mode and market_volatility > 0.7 and avg_confidence >= 0.75:
            guards_should_attack = True
            logger.info(f"⚔️ VOLATILITÉ EXTRÊME! Vol: {market_volatility:.2f} - GUARDS ATTACK!")
        
        if guards_should_attack and target_guards > 0:
            for guard in guards[:target_guards]:
                if len(guard.current_trades) > 0:
                    continue  # Skip si déjà en trade
                
                # Les guards utilisent le signal dominant
                signal = dominant_signal
                confidence = avg_confidence
                
                # Valider avec le Guardian
                approved, volume, stop_loss, take_profit = self.guardian.validate_trade(
                    guard, signal, confidence, current_price, atr
                )
                
                if approved:
                    # GUARDS: lots augmentés (attaque)
                    guard_volume = volume * 1.5
                    
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
        
        # Compter les positions après déploiement
        total_positions_after = sum(len(bee.current_trades) for bee in self.bees)
        
        if total_positions_after > total_open_positions:
            new_positions = total_positions_after - total_open_positions
            logger.info(f"🔥 {new_positions} nouvelles positions ouvertes!")
            
            if total_positions_after >= 15:
                logger.info(f"💥 ATTAQUE MASSIVE! {total_positions_after} positions actives!")
        
        # Mettre à jour les positions ouvertes
        self._update_open_positions()
        
        # Évolution de l'essaim
        if self.generation % 10 == 0 and self.generation > 0:
            self._evolve_swarm()
        
        self.generation += 1
        time.sleep(1)
    
    def _update_open_positions(self):
        """Mettre à jour toutes les positions ouvertes avec MODES ADAPTATIFS"""
        current_price = self.field.get_current_price()
        current_time = datetime.now()
        
        # Calculer la volatilité du marché
        market_volatility = self._calculate_market_volatility()
        
        # Déterminer le mode: RÉCOLTE (calme) ou GUERRIER (volatil)
        is_warrior_mode = market_volatility > 0.5  # Seuil de volatilité
        mode_name = "⚔️ GUERRIER" if is_warrior_mode else "🌾 RÉCOLTE"
        
        # Seuils de profit adaptatifs
        profit_threshold = 0.10 if not is_warrior_mode else 0.15  # Plus exigeant en mode guerrier
        max_loss_threshold = -0.20 if not is_warrior_mode else -0.30  # Plus tolérant en mode guerrier
        max_time_in_trade = 30 if not is_warrior_mode else 60  # Plus rapide en mode récolte
        
        # Compter les positions ouvertes totales
        total_open_positions = sum(len(bee.current_trades) for bee in self.bees)
        
        # Si trop de positions ouvertes (blocage), forcer des fermetures
        if total_open_positions >= 15:
            logger.warning(f"🚨 BLOCAGE DÉTECTÉ: {total_open_positions} positions ouvertes!")
            logger.warning("🛡️ Libération de slots pour les guerrières...")
            self._force_close_blocking_positions()
        
        for bee in self.bees:
            for trade in bee.current_trades[:]:
                # Vérifier si la position est toujours ouverte sur MT5
                positions = mt5.positions_get(ticket=trade.ticket)
                
                if positions is None or len(positions) == 0:
                    # Position fermée par MT5 (SL/TP)
                    pnl = trade.calculate_pnl(current_price)
                    
                    trade.exit_price = current_price
                    trade.exit_time = current_time
                    trade.pnl = pnl
                    trade.status = "CLOSED"
                    
                    # Mettre à jour les statistiques
                    bee.current_trades.remove(trade)
                    bee.trade_history.append(trade)
                    bee.update_performance()
                    self.guardian.update_capital(pnl)
                    
                    logger.info(f"💰 {bee.bee_id} - Trade closed by MT5: PnL = ${pnl:.2f}")
                else:
                    # Position ouverte - GESTION ADAPTATIVE !
                    position = positions[0]
                    current_pnl = position.profit
                    time_in_trade = (current_time - trade.entry_time).total_seconds()
                    
                    # 🐝 RÈGLE 1: FERMETURE À +€0.10 MINIMUM (PRIORITÉ ABSOLUE !)
                    if current_pnl >= profit_threshold:
                        logger.info(f"🐝 {mode_name} - {bee.bee_id} - Nectar collected: ${current_pnl:.2f}")
                        if self.field.close_position(trade.ticket):
                            trade.exit_price = current_price
                            trade.exit_time = current_time
                            trade.pnl = current_pnl
                            trade.status = "CLOSED_PROFIT"
                            bee.current_trades.remove(trade)
                            bee.trade_history.append(trade)
                            bee.update_performance()
                            self.guardian.update_capital(current_pnl)
                            logger.info(f"✅ {bee.bee_id} - Profit secured: ${current_pnl:.2f}")
                    
                    # 🛡️ RÈGLE 2: COUPE-PERTE ADAPTATIVE
                    elif current_pnl <= max_loss_threshold:
                        logger.warning(f"🛡️ {mode_name} - {bee.bee_id} - Danger: ${current_pnl:.2f}")
                        if self.field.close_position(trade.ticket):
                            trade.exit_price = current_price
                            trade.exit_time = current_time
                            trade.pnl = current_pnl
                            trade.status = "CLOSED_LOSS"
                            bee.current_trades.remove(trade)
                            bee.trade_history.append(trade)
                            bee.update_performance()
                            self.guardian.update_capital(current_pnl)
                            logger.info(f"🛡️ {bee.bee_id} - Loss cut: ${current_pnl:.2f}")
                    
                    # ⚡ RÈGLE 3: SIGNAL CONTRAIRE → SORTIE
                    elif current_pnl > 0 and hasattr(bee, 'generate_signal'):
                        signal_data = bee.generate_signal()
                        if signal_data:
                            current_signal = signal_data.get('type', 'HOLD')
                            
                            # Si le signal change, rentrer avec ce qu'on a !
                            if (trade.order_type == 'SELL' and current_signal == 'BUY') or \
                               (trade.order_type == 'BUY' and current_signal == 'SELL'):
                                logger.info(f"⚡ {bee.bee_id} - Signal reversed: ${current_pnl:.2f}")
                                if self.field.close_position(trade.ticket):
                                    trade.exit_price = current_price
                                    trade.exit_time = current_time
                                    trade.pnl = current_pnl
                                    trade.status = "CLOSED_SIGNAL"
                                    bee.current_trades.remove(trade)
                                    bee.trade_history.append(trade)
                                    bee.update_performance()
                                    self.guardian.update_capital(current_pnl)
                    
                    # ⏱️ RÈGLE 4: TIMEOUT ADAPTATIF
                    elif time_in_trade >= max_time_in_trade:
                        logger.info(f"⏱️ {mode_name} - {bee.bee_id} - Timeout ({time_in_trade:.0f}s): ${current_pnl:.2f}")
                        if self.field.close_position(trade.ticket):
                            trade.exit_price = current_price
                            trade.exit_time = current_time
                            trade.pnl = current_pnl
                            trade.status = "CLOSED_TIMEOUT"
                            bee.current_trades.remove(trade)
                            bee.trade_history.append(trade)
                            bee.update_performance()
                            self.guardian.update_capital(current_pnl)
    
    def _calculate_market_volatility(self):
        """Calculer la volatilité du marché pour déterminer le mode"""
        try:
            # Récupérer les dernières bougies
            rates = mt5.copy_rates_from_pos(self.field.symbol, mt5.TIMEFRAME_M1, 0, 20)
            
            if rates is None or len(rates) < 20:
                return 0.3  # Valeur par défaut
            
            # Calculer ATR simplifié (Average True Range)
            high_low = [r['high'] - r['low'] for r in rates]
            atr = sum(high_low) / len(high_low)
            
            # Normaliser (pour XAUUSD, ATR normal ~1.0-3.0)
            normalized_volatility = min(atr / 2.0, 1.0)
            
            logger.info(f"📊 Market volatility: {normalized_volatility:.2f} (ATR: {atr:.2f})")
            
            return normalized_volatility
            
        except Exception as e:
            logger.error(f"❌ Error calculating volatility: {e}")
            return 0.3  # Valeur par défaut
    
    def _activate_bees_by_type(self, bee_type: str, target_count: int):
        """Activer/désactiver abeilles pour atteindre target_count actives"""
        
        # Filtrer les abeilles du bon type
        bees_of_type = [bee for bee in self.bees if bee.bee_type == bee_type]
        
        # Compter combien sont déjà actives
        active_bees = [bee for bee in bees_of_type if bee.active]
        active_count = len(active_bees)
        
        if target_count > active_count:
            # Besoin d'activer plus d'abeilles
            needed = target_count - active_count
            inactive_bees = [bee for bee in bees_of_type if not bee.active]
            
            for bee in inactive_bees[:needed]:
                bee.active = True
                logger.info(f"✅ {bee.bee_id} activated ({bee_type})")
        
        elif target_count < active_count:
            # Besoin de désactiver des abeilles (les moins performantes)
            to_deactivate = active_count - target_count
            
            # Trier par performance (fitness_score)
            sorted_active = sorted(active_bees, key=lambda b: b.performance.fitness_score)
            
            for bee in sorted_active[:to_deactivate]:
                # Fermer ses positions d'abord
                for trade in list(bee.current_trades):
                    try:
                        self.field.close_position(trade.ticket)
                    except:
                        pass
                
                bee.active = False
                logger.info(f"💤 {bee.bee_id} deactivated ({bee_type})")
    
    def _force_close_blocking_positions(self):
        """Fermer les positions les plus faibles pour libérer des slots"""
        # Collecter toutes les positions avec leur PnL
        all_positions = []
        for bee in self.bees:
            for trade in bee.current_trades:
                positions = mt5.positions_get(ticket=trade.ticket)
                if positions and len(positions) > 0:
                    all_positions.append({
                        'bee': bee,
                        'trade': trade,
                        'pnl': positions[0].profit,
                        'ticket': trade.ticket
                    })
        
        # Trier par PnL (les pires d'abord)
        all_positions.sort(key=lambda x: x['pnl'])
        
        # Fermer les 5 pires positions
        closed_count = 0
        for pos in all_positions[:5]:
            logger.warning(f"🛡️ Force closing {pos['bee'].bee_id} - PnL: ${pos['pnl']:.2f}")
            
            if self.field.close_position(pos['ticket']):
                trade = pos['trade']
                trade.exit_price = self.field.get_current_price()
                trade.exit_time = datetime.now()
                trade.pnl = pos['pnl']
                trade.status = "CLOSED_FORCED"
                
                pos['bee'].current_trades.remove(trade)
                pos['bee'].trade_history.append(trade)
                pos['bee'].update_performance()
                self.guardian.update_capital(pos['pnl'])
                
                closed_count += 1
        
        logger.info(f"✅ Forced closure: {closed_count} positions freed")
    
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
        
        # CORRECTION: Garder 50% des meilleures (pas 75%)
        # Et éliminer seulement les très faibles (fitness < -0.3)
        cutoff = len(self.bees) // 2  # Garder top 50%
        weak_bees = [bee for bee in self.bees[cutoff:] if bee.performance.fitness_score < -0.3]
        
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
