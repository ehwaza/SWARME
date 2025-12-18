"""
🌐 SWARNE V2.0 - Multi-Symbol Manager
Gestion du trading sur plusieurs symboles avec analyse de corrélation
"""

import numpy as np
import pandas as pd
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class CorrelationAnalyzer:
    """Analyseur de corrélations entre symboles"""
    
    def __init__(self):
        self.correlation_matrix = {}
        self.price_history = {}
        
    def update(self, symbol: str, price: float):
        """Mettre à jour l'historique de prix"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(price)
        
        # Garder seulement les 100 derniers prix
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
    
    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """Calculer la matrice de corrélation"""
        symbols = list(self.price_history.keys())
        
        if len(symbols) < 2:
            return pd.DataFrame()
        
        # Créer DataFrame avec les prix
        df_dict = {}
        for symbol in symbols:
            df_dict[symbol] = self.price_history[symbol][-100:]  # Derniers 100
        
        df = pd.DataFrame(df_dict)
        
        # Calculer corrélation
        corr_matrix = df.corr()
        
        return corr_matrix
    
    def get_correlation(self, symbol1: str, symbol2: str) -> float:
        """Obtenir la corrélation entre 2 symboles"""
        corr_matrix = self.calculate_correlation_matrix()
        
        if symbol1 not in corr_matrix.columns or symbol2 not in corr_matrix.columns:
            return 0.0
        
        return corr_matrix.loc[symbol1, symbol2]


class MultiSymbolManager:
    """Gestionnaire multi-symboles"""
    
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.correlation_analyzer = CorrelationAnalyzer()
        self.open_positions = {symbol: [] for symbol in symbols}
        
    def update_prices(self, prices: Dict[str, float]):
        """Mettre à jour les prix de tous les symboles"""
        for symbol, price in prices.items():
            if symbol in self.symbols:
                self.correlation_analyzer.update(symbol, price)
    
    def check_correlation_risk(self, symbol: str) -> float:
        """Vérifier le risque de corrélation"""
        # Calculer corrélation avec positions ouvertes
        correlations = []
        
        for other_symbol in self.symbols:
            if other_symbol == symbol:
                continue
            
            if len(self.open_positions[other_symbol]) > 0:
                corr = self.correlation_analyzer.get_correlation(symbol, other_symbol)
                correlations.append(abs(corr))
        
        if not correlations:
            return 0.0
        
        # Risque = corrélation moyenne
        return np.mean(correlations)
    
    def add_position(self, symbol: str, trade):
        """Ajouter une position"""
        if symbol in self.open_positions:
            self.open_positions[symbol].append(trade)
            logger.info(f"📊 Position added: {symbol}")
    
    def remove_position(self, symbol: str, trade):
        """Retirer une position"""
        if symbol in self.open_positions and trade in self.open_positions[symbol]:
            self.open_positions[symbol].remove(trade)
            logger.info(f"📊 Position removed: {symbol}")
    
    def get_exposure(self) -> Dict[str, float]:
        """Obtenir l'exposition par symbole"""
        exposure = {}
        
        for symbol in self.symbols:
            total_volume = sum(trade.volume for trade in self.open_positions[symbol])
            exposure[symbol] = total_volume
        
        return exposure
    
    def optimize_allocation(self, capital: float) -> Dict[str, float]:
        """Optimiser l'allocation du capital"""
        # Allocation simple: équipondérée
        num_symbols = len(self.symbols)
        allocation = {symbol: capital / num_symbols for symbol in self.symbols}
        
        return allocation
