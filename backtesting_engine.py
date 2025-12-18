"""
📊 SWARNE V2.0 - Backtesting Engine
Moteur de backtest vectorisé avec métriques avancées
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging

# Import MT5 utilities
try:
    from mt5_utils import (
        mt5_to_pandas_timeframe, 
        normalize_symbol,
        load_mt5_data
    )
    MT5_UTILS_AVAILABLE = True
except ImportError:
    MT5_UTILS_AVAILABLE = False
    print("⚠️  mt5_utils not found, using fallback conversions")

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Configuration du backtest"""
    start_date: str = "2023-01-01"
    end_date: str = "2024-12-16"
    symbols: List[str] = field(default_factory=lambda: ["EURUSD"])
    initial_capital: float = 10000.0
    commission: float = 0.0001  # 1 pip
    slippage: float = 0.0001    # 1 pip
    timeframe: str = "H1"        # Timeframe
    
    # Risk management
    max_position_size: float = 0.1  # 10% du capital max par trade
    max_daily_loss: float = 0.03    # 3% perte max par jour


@dataclass
class Trade:
    """Représentation d'un trade"""
    entry_time: datetime
    exit_time: Optional[datetime] = None
    symbol: str = "EURUSD"
    direction: str = "BUY"  # BUY ou SELL
    entry_price: float = 0.0
    exit_price: float = 0.0
    volume: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    commission: float = 0.0
    bee_id: str = ""
    
    def close(self, exit_price: float, exit_time: datetime, commission: float = 0.0):
        """Fermer le trade"""
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.commission = commission
        
        # Calculer P&L
        if self.direction == "BUY":
            self.pnl = (exit_price - self.entry_price) * self.volume - commission
        else:  # SELL
            self.pnl = (self.entry_price - exit_price) * self.volume - commission
        
        self.pnl_pct = (self.pnl / (self.entry_price * self.volume)) * 100 if self.volume > 0 else 0


@dataclass
class BacktestResults:
    """Résultats du backtest"""
    # Métriques de base
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    
    # P&L
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    profit_factor: float = 0.0
    
    # Capital
    initial_capital: float = 0.0
    final_capital: float = 0.0
    max_capital: float = 0.0
    min_capital: float = 0.0
    
    # Drawdown
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    avg_drawdown: float = 0.0
    
    # Ratios de performance
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    
    # Statistiques des trades
    avg_trade_pnl: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    
    # Durée
    avg_trade_duration: timedelta = timedelta(0)
    max_trade_duration: timedelta = timedelta(0)
    
    # Equity curve
    equity_curve: List[float] = field(default_factory=list)
    dates: List[datetime] = field(default_factory=list)
    
    # Trades détaillés
    trades: List[Trade] = field(default_factory=list)


class BacktestEngine:
    """Moteur de backtesting"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.data = {}
        self.results = BacktestResults()
        
    def load_data(self, symbol: str) -> pd.DataFrame:
        """Charger les données historiques"""
        logger.info(f"📥 Loading historical data for {symbol}")
        
        # Normaliser le symbole
        if MT5_UTILS_AVAILABLE:
            symbol = normalize_symbol(symbol)
        else:
            symbol = symbol.upper()
        
        # Essayer de charger depuis MT5
        if MT5_UTILS_AVAILABLE:
            df = load_mt5_data(symbol, self.config.timeframe, num_bars=20000)
            
            if df is not None and len(df) > 0:
                # Filtrer par dates
                start = pd.to_datetime(self.config.start_date)
                end = pd.to_datetime(self.config.end_date)
                
                df = df[(df['time'] >= start) & (df['time'] <= end)]
                
                if len(df) > 0:
                    self.data[symbol] = df
                    logger.info(f"✅ Loaded {len(df)} bars for {symbol}")
                    return df
        
        # Fallback: Générer données simulées
        logger.warning(f"⚠️  Using simulated data for {symbol}")
        
        start = pd.to_datetime(self.config.start_date)
        end = pd.to_datetime(self.config.end_date)
        
        # Convertir timeframe MT5 → Pandas
        if MT5_UTILS_AVAILABLE:
            pandas_tf = mt5_to_pandas_timeframe(self.config.timeframe)
        else:
            # Conversion manuelle simple
            tf_map = {
                'M1': '1min', 'M5': '5min', 'M15': '15min', 'M30': '30min',
                'H1': '1H', 'H4': '4H', 'D1': '1D'
            }
            pandas_tf = tf_map.get(self.config.timeframe.upper(), '1H')
        
        dates = pd.date_range(start, end, freq=pandas_tf)
        
        # Prix simulé avec marche aléatoire
        np.random.seed(42)
        base_price = 1.1800 if symbol == "EURUSD" else 1.2500
        returns = np.random.normal(0.0001, 0.01, len(dates))
        prices = base_price * np.cumprod(1 + returns)
        
        df = pd.DataFrame({
            'time': dates,
            'open': prices * (1 + np.random.uniform(-0.001, 0.001, len(dates))),
            'high': prices * (1 + np.random.uniform(0, 0.002, len(dates))),
            'low': prices * (1 + np.random.uniform(-0.002, 0, len(dates))),
            'close': prices,
            'volume': np.random.randint(100, 1000, len(dates))
        })
        
        self.data[symbol] = df
        logger.info(f"✅ Generated {len(df)} bars for {symbol}")
        
        return df
    
    def run(self, hive) -> BacktestResults:
        """Exécuter le backtest"""
        logger.info("🚀 Starting backtest...")
        
        # Charger les données
        for symbol in self.config.symbols:
            self.load_data(symbol)
        
        # Initialiser
        self.results.initial_capital = self.config.initial_capital
        current_capital = self.config.initial_capital
        open_trades = []
        
        equity_curve = [current_capital]
        dates = [pd.to_datetime(self.config.start_date)]
        
        # Itérer sur les barres
        main_symbol = self.config.symbols[0]
        df = self.data[main_symbol]
        
        for i in range(100, len(df)):  # Démarrer après 100 barres pour indicateurs
            current_time = df.iloc[i]['time']
            current_price = df.iloc[i]['close']
            
            # Construire les données du marché jusqu'à ce point
            market_data = df.iloc[:i+1].copy()
            
            # Vérifier les trades ouverts (stop-loss, take-profit)
            for trade in open_trades[:]:
                should_close = False
                exit_price = current_price
                
                if trade.direction == "BUY":
                    # Check stop-loss
                    if current_price <= trade.stop_loss:
                        should_close = True
                        exit_price = trade.stop_loss
                    # Check take-profit
                    elif current_price >= trade.take_profit:
                        should_close = True
                        exit_price = trade.take_profit
                else:  # SELL
                    # Check stop-loss
                    if current_price >= trade.stop_loss:
                        should_close = True
                        exit_price = trade.stop_loss
                    # Check take-profit
                    elif current_price <= trade.take_profit:
                        should_close = True
                        exit_price = trade.take_profit
                
                if should_close:
                    # Appliquer commission + slippage
                    commission = trade.volume * self.config.commission
                    exit_price += self.config.slippage if trade.direction == "BUY" else -self.config.slippage
                    
                    trade.close(exit_price, current_time, commission)
                    current_capital += trade.pnl
                    
                    open_trades.remove(trade)
                    self.results.trades.append(trade)
            
            # Chaque bee analyse le marché
            for bee in hive.bees:
                # Analyser le marché
                signal, confidence = bee.analyze_market(market_data)
                
                # Vérifier si un signal est généré
                if signal in ["BUY", "SELL"] and confidence >= 0.5:
                    # Calculer ATR pour stop-loss
                    atr = self._calculate_atr(market_data, period=14)
                    
                    # Demander validation au Guardian
                    approved, volume, sl, tp = hive.guardian.validate_trade(
                        bee, signal, confidence, current_price, atr
                    )
                    
                    if approved and volume > 0:
                        # Créer le trade
                        trade = Trade(
                            entry_time=current_time,
                            symbol=main_symbol,
                            direction=signal,
                            entry_price=current_price,
                            volume=volume,
                            stop_loss=sl,
                            take_profit=tp,
                            bee_id=bee.bee_id
                        )
                        
                        open_trades.append(trade)
            
            # Mettre à jour la courbe d'equity
            total_open_pnl = sum(self._calculate_open_pnl(t, current_price) 
                                for t in open_trades)
            equity = current_capital + total_open_pnl
            
            equity_curve.append(equity)
            dates.append(current_time)
        
        # Fermer tous les trades ouverts à la fin
        final_price = df.iloc[-1]['close']
        final_time = df.iloc[-1]['time']
        
        for trade in open_trades:
            trade.close(final_price, final_time, 
                       trade.volume * self.config.commission)
            current_capital += trade.pnl
            self.results.trades.append(trade)
        
        # Calculer les métriques
        self.results.equity_curve = equity_curve
        self.results.dates = dates
        self.results.final_capital = current_capital
        self._calculate_metrics()
        
        logger.info("✅ Backtest completed!")
        logger.info(f"📊 Total trades: {self.results.total_trades}")
        logger.info(f"💰 Final capital: ${self.results.final_capital:,.2f}")
        logger.info(f"📈 Return: {self.results.total_pnl_pct:.2f}%")
        logger.info(f"🎯 Win rate: {self.results.win_rate:.1f}%")
        logger.info(f"📉 Max drawdown: {self.results.max_drawdown_pct:.2f}%")
        logger.info(f"⚡ Sharpe ratio: {self.results.sharpe_ratio:.2f}")
        
        return self.results
    
    def _calculate_open_pnl(self, trade: Trade, current_price: float) -> float:
        """Calculer le P&L d'un trade ouvert"""
        if trade.direction == "BUY":
            return (current_price - trade.entry_price) * trade.volume
        else:
            return (trade.entry_price - current_price) * trade.volume
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculer l'ATR"""
        if len(df) < period + 1:
            return 0.0015  # Valeur par défaut
        
        high = df['high'].values[-period-1:]
        low = df['low'].values[-period-1:]
        close = df['close'].values[-period-1:]
        
        tr1 = high[1:] - low[1:]
        tr2 = np.abs(high[1:] - close[:-1])
        tr3 = np.abs(low[1:] - close[:-1])
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr = np.mean(tr)
        
        return atr
    
    def _calculate_metrics(self):
        """Calculer toutes les métriques de performance"""
        trades = self.results.trades
        
        if not trades:
            logger.warning("⚠️ No trades to analyze")
            return
        
        # Métriques de base
        self.results.total_trades = len(trades)
        self.results.winning_trades = sum(1 for t in trades if t.pnl > 0)
        self.results.losing_trades = sum(1 for t in trades if t.pnl < 0)
        self.results.win_rate = (self.results.winning_trades / self.results.total_trades * 100 
                                if self.results.total_trades > 0 else 0)
        
        # P&L
        self.results.total_pnl = sum(t.pnl for t in trades)
        self.results.total_pnl_pct = ((self.results.final_capital - self.results.initial_capital) / 
                                     self.results.initial_capital * 100)
        
        self.results.gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
        self.results.gross_loss = abs(sum(t.pnl for t in trades if t.pnl < 0))
        self.results.profit_factor = (self.results.gross_profit / self.results.gross_loss 
                                     if self.results.gross_loss > 0 else 0)
        
        # Statistiques des trades
        self.results.avg_trade_pnl = self.results.total_pnl / self.results.total_trades
        
        winning_pnls = [t.pnl for t in trades if t.pnl > 0]
        losing_pnls = [t.pnl for t in trades if t.pnl < 0]
        
        self.results.avg_win = np.mean(winning_pnls) if winning_pnls else 0
        self.results.avg_loss = np.mean(losing_pnls) if losing_pnls else 0
        self.results.largest_win = max(winning_pnls) if winning_pnls else 0
        self.results.largest_loss = min(losing_pnls) if losing_pnls else 0
        
        # Durée des trades
        durations = [(t.exit_time - t.entry_time) for t in trades if t.exit_time]
        self.results.avg_trade_duration = (sum(durations, timedelta()) / len(durations) 
                                          if durations else timedelta(0))
        self.results.max_trade_duration = max(durations) if durations else timedelta(0)
        
        # Drawdown
        equity = np.array(self.results.equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = equity - running_max
        drawdown_pct = (drawdown / running_max) * 100
        
        self.results.max_capital = float(running_max[-1])
        self.results.min_capital = float(equity.min())
        self.results.max_drawdown = float(drawdown.min())
        self.results.max_drawdown_pct = float(drawdown_pct.min())
        self.results.avg_drawdown = float(drawdown.mean())
        
        # Ratios de performance
        returns = np.diff(equity) / equity[:-1]
        
        if len(returns) > 0:
            # Sharpe Ratio (annualisé, supposant trading horaire)
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            
            if std_return > 0:
                # 252 jours de trading * 24 heures (approximation)
                self.results.sharpe_ratio = (mean_return / std_return) * np.sqrt(252 * 24)
            
            # Sortino Ratio (utilise seulement la downside volatility)
            downside_returns = returns[returns < 0]
            if len(downside_returns) > 0:
                downside_std = np.std(downside_returns)
                if downside_std > 0:
                    self.results.sortino_ratio = (mean_return / downside_std) * np.sqrt(252 * 24)
            
            # Calmar Ratio (Return / Max Drawdown)
            if abs(self.results.max_drawdown_pct) > 0:
                self.results.calmar_ratio = (self.results.total_pnl_pct / 
                                            abs(self.results.max_drawdown_pct))
    
    def generate_report(self, filename: str = "backtest_report.html"):
        """Générer un rapport HTML"""
        # TODO: Implémenter génération rapport HTML avec plotly
        logger.info(f"📄 Generating report: {filename}")
        pass
    
    def plot_equity_curve(self):
        """Tracer la courbe d'equity"""
        # TODO: Implémenter avec matplotlib ou plotly
        pass


# ================================================================
# WALK-FORWARD ANALYSIS
# ================================================================

class WalkForwardAnalysis:
    """Analyse walk-forward pour validation robuste"""
    
    def __init__(self, train_period_days: int = 180, 
                 test_period_days: int = 60):
        self.train_period = train_period_days
        self.test_period = test_period_days
        
    def run(self, start_date: str, end_date: str, hive):
        """Exécuter l'analyse walk-forward"""
        logger.info("🔄 Starting walk-forward analysis...")
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        results = []
        current_start = start
        
        while current_start + timedelta(days=self.train_period + self.test_period) <= end:
            train_end = current_start + timedelta(days=self.train_period)
            test_end = train_end + timedelta(days=self.test_period)
            
            logger.info(f"📊 Period: {current_start.date()} -> {test_end.date()}")
            
            # 1. Entraîner sur la période de train
            train_config = BacktestConfig(
                start_date=current_start.strftime("%Y-%m-%d"),
                end_date=train_end.strftime("%Y-%m-%d")
            )
            
            # 2. Tester sur la période de test
            test_config = BacktestConfig(
                start_date=train_end.strftime("%Y-%m-%d"),
                end_date=test_end.strftime("%Y-%m-%d")
            )
            
            test_engine = BacktestEngine(test_config)
            test_results = test_engine.run(hive)
            
            results.append({
                'period': f"{train_end.date()} - {test_end.date()}",
                'return': test_results.total_pnl_pct,
                'sharpe': test_results.sharpe_ratio,
                'max_dd': test_results.max_drawdown_pct,
                'win_rate': test_results.win_rate
            })
            
            # Prochaine période
            current_start = test_end
        
        logger.info(f"✅ Walk-forward completed: {len(results)} periods")
        
        return results
