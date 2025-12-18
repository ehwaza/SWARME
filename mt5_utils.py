"""
🔧 SWARNE V2.0 - MT5 Utilities
Utilitaires pour conversion et gestion MT5
"""

import MetaTrader5 as mt5
import pandas as pd
from typing import Optional, Dict


# ============================================================
# CONVERSION TIMEFRAMES
# ============================================================

# Mapping MT5 → Pandas
MT5_TO_PANDAS_TIMEFRAME = {
    'M1': '1min',
    'M5': '5min',
    'M15': '15min',
    'M30': '30min',
    'H1': '1H',
    'H4': '4H',
    'D1': '1D',
    'W1': '1W',
    'MN1': '1M'
}

# Mapping Pandas → MT5
PANDAS_TO_MT5_TIMEFRAME = {v: k for k, v in MT5_TO_PANDAS_TIMEFRAME.items()}

# Mapping MT5 String → MT5 Constant
MT5_TIMEFRAME_CONSTANTS = {
    'M1': mt5.TIMEFRAME_M1,
    'M5': mt5.TIMEFRAME_M5,
    'M15': mt5.TIMEFRAME_M15,
    'M30': mt5.TIMEFRAME_M30,
    'H1': mt5.TIMEFRAME_H1,
    'H4': mt5.TIMEFRAME_H4,
    'D1': mt5.TIMEFRAME_D1,
    'W1': mt5.TIMEFRAME_W1,
    'MN1': mt5.TIMEFRAME_MN1
}


def mt5_to_pandas_timeframe(mt5_tf: str) -> str:
    """
    Convertir timeframe MT5 (H1, M15...) vers format Pandas (1H, 15min...)
    
    Args:
        mt5_tf: Timeframe MT5 (ex: "H1", "M15")
    
    Returns:
        Timeframe Pandas (ex: "1H", "15min")
    """
    mt5_tf = mt5_tf.upper()
    
    if mt5_tf in MT5_TO_PANDAS_TIMEFRAME:
        return MT5_TO_PANDAS_TIMEFRAME[mt5_tf]
    
    # Fallback: essayer de déduire
    if mt5_tf.startswith('M'):
        minutes = mt5_tf[1:]
        return f"{minutes}min"
    elif mt5_tf.startswith('H'):
        hours = mt5_tf[1:]
        return f"{hours}H"
    elif mt5_tf.startswith('D'):
        return "1D"
    elif mt5_tf.startswith('W'):
        return "1W"
    
    # Dernier recours
    return "1H"


def pandas_to_mt5_timeframe(pandas_tf: str) -> str:
    """
    Convertir timeframe Pandas (1H, 15min...) vers format MT5 (H1, M15...)
    
    Args:
        pandas_tf: Timeframe Pandas (ex: "1H", "15min")
    
    Returns:
        Timeframe MT5 (ex: "H1", "M15")
    """
    if pandas_tf in PANDAS_TO_MT5_TIMEFRAME:
        return PANDAS_TO_MT5_TIMEFRAME[pandas_tf]
    
    # Fallback
    return "H1"


def get_mt5_timeframe_constant(timeframe: str):
    """
    Obtenir la constante MT5 pour un timeframe
    
    Args:
        timeframe: Timeframe string (ex: "H1", "M15")
    
    Returns:
        Constante MT5 (ex: mt5.TIMEFRAME_H1)
    """
    timeframe = timeframe.upper()
    
    if timeframe in MT5_TIMEFRAME_CONSTANTS:
        return MT5_TIMEFRAME_CONSTANTS[timeframe]
    
    # Fallback
    return mt5.TIMEFRAME_H1


# ============================================================
# NORMALISATION SYMBOLES
# ============================================================

def normalize_symbol(symbol: str) -> str:
    """
    Normaliser un symbole pour MT5
    
    Args:
        symbol: Symbole (ex: "eurusd", "EURUSD", "EURusd")
    
    Returns:
        Symbole normalisé en majuscules (ex: "EURUSD")
    """
    return symbol.upper().strip()


def validate_symbol(symbol: str) -> bool:
    """
    Vérifier si un symbole existe dans MT5
    
    Args:
        symbol: Symbole à vérifier
    
    Returns:
        True si le symbole existe, False sinon
    """
    normalized = normalize_symbol(symbol)
    
    # Vérifier si MT5 est initialisé
    if not mt5.initialize():
        return False
    
    # Vérifier le symbole
    symbol_info = mt5.symbol_info(normalized)
    
    return symbol_info is not None


# ============================================================
# CHARGEMENT DONNÉES MT5
# ============================================================

def load_mt5_data(symbol: str, timeframe: str, num_bars: int = 10000) -> Optional[pd.DataFrame]:
    """
    Charger des données historiques depuis MT5
    
    Args:
        symbol: Symbole (sera normalisé)
        timeframe: Timeframe MT5 (ex: "H1", "M15")
        num_bars: Nombre de barres à charger
    
    Returns:
        DataFrame avec colonnes: time, open, high, low, close, volume
        None si erreur
    """
    # Normaliser
    symbol = normalize_symbol(symbol)
    timeframe_constant = get_mt5_timeframe_constant(timeframe)
    
    # Initialiser MT5
    if not mt5.initialize():
        print(f"❌ Impossible d'initialiser MT5")
        print(f"💡 Ouvrez MetaTrader 5 et connectez-vous")
        return None
    
    # Vérifier le symbole
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"❌ Symbole invalide: {symbol}")
        
        # Lister quelques symboles disponibles
        all_symbols = mt5.symbols_get()
        if all_symbols and len(all_symbols) > 0:
            available = [s.name for s in all_symbols[:10]]
            print(f"💡 Symboles disponibles: {', '.join(available)}...")
        
        mt5.shutdown()
        return None
    
    # Sélectionner le symbole (critique !)
    if not mt5.symbol_select(symbol, True):
        print(f"⚠️  Impossible de sélectionner {symbol}, tentative quand même...")
    
    # Charger les données
    rates = mt5.copy_rates_from_pos(symbol, timeframe_constant, 0, num_bars)
    
    if rates is None or len(rates) == 0:
        error = mt5.last_error()
        print(f"❌ Impossible de charger les données pour {symbol}")
        print(f"   Erreur MT5: {error}")
        print(f"💡 Essayez:")
        print(f"   1. Ouvrir un graphique {symbol} dans MT5")
        print(f"   2. Attendre que l'historique se charge")
        print(f"   3. Relancer l'opération")
        mt5.shutdown()
        return None
    
    # Convertir en DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Renommer tick_volume en volume (standard MT5)
    if 'tick_volume' in df.columns and 'volume' not in df.columns:
        df['volume'] = df['tick_volume']
    
    # S'assurer qu'on a les colonnes essentielles
    required_cols = ['time', 'open', 'high', 'low', 'close', 'volume']
    missing = [col for col in required_cols if col not in df.columns]
    
    if missing:
        print(f"⚠️  Colonnes manquantes: {missing}")
        print(f"   Colonnes disponibles: {list(df.columns)}")
    
    mt5.shutdown()
    
    print(f"✅ {len(df)} barres chargées pour {symbol} ({timeframe})")
    
    return df


def get_available_symbols() -> list:
    """
    Obtenir la liste des symboles disponibles dans MT5
    
    Returns:
        Liste des symboles
    """
    if not mt5.initialize():
        return []
    
    symbols = mt5.symbols_get()
    
    if symbols is None:
        mt5.shutdown()
        return []
    
    symbol_names = [s.name for s in symbols]
    
    mt5.shutdown()
    
    return symbol_names


# ============================================================
# INFORMATIONS MARCHÉ
# ============================================================

def get_current_price(symbol: str) -> Optional[float]:
    """
    Obtenir le prix actuel d'un symbole
    
    Args:
        symbol: Symbole
    
    Returns:
        Prix actuel (bid) ou None si erreur
    """
    symbol = normalize_symbol(symbol)
    
    if not mt5.initialize():
        return None
    
    tick = mt5.symbol_info_tick(symbol)
    
    mt5.shutdown()
    
    if tick is None:
        return None
    
    return tick.bid


def get_symbol_info_dict(symbol: str) -> Optional[Dict]:
    """
    Obtenir les informations d'un symbole
    
    Args:
        symbol: Symbole
    
    Returns:
        Dictionnaire avec infos du symbole
    """
    symbol = normalize_symbol(symbol)
    
    if not mt5.initialize():
        return None
    
    info = mt5.symbol_info(symbol)
    
    mt5.shutdown()
    
    if info is None:
        return None
    
    return {
        'name': info.name,
        'description': info.description,
        'point': info.point,
        'digits': info.digits,
        'spread': info.spread,
        'volume_min': info.volume_min,
        'volume_max': info.volume_max,
        'volume_step': info.volume_step,
        'trade_contract_size': info.trade_contract_size
    }


# ============================================================
# HELPERS
# ============================================================

def timeframe_to_seconds(timeframe: str) -> int:
    """
    Convertir un timeframe en secondes
    
    Args:
        timeframe: Timeframe MT5 (ex: "H1", "M15")
    
    Returns:
        Nombre de secondes
    """
    timeframe = timeframe.upper()
    
    timeframe_seconds = {
        'M1': 60,
        'M5': 300,
        'M15': 900,
        'M30': 1800,
        'H1': 3600,
        'H4': 14400,
        'D1': 86400,
        'W1': 604800,
        'MN1': 2592000
    }
    
    return timeframe_seconds.get(timeframe, 3600)


def format_price(price: float, digits: int = 5) -> str:
    """
    Formater un prix avec le bon nombre de décimales
    
    Args:
        price: Prix
        digits: Nombre de décimales
    
    Returns:
        Prix formaté
    """
    return f"{price:.{digits}f}"
