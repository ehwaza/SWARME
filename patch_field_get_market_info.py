"""
SWARNE FIX - Patch Field.get_market_info()

Ajoute la méthode get_market_info() à la classe Field
"""

import numpy as np
import MetaTrader5 as mt5

def patch_field_add_get_market_info(field):
    """
    Ajoute la méthode get_market_info() à un objet Field
    """
    
    def get_market_info(self):
        """
        Récupère les informations du marché
        
        Returns:
            dict: {
                'price': float,
                'atr': float,
                'spread': float,
                'trend': str,
                'volatility': float
            }
        """
        try:
            # Récupérer le prix actuel
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                return None
            
            price = tick.bid
            spread = (tick.ask - tick.bid) / tick.bid if tick.bid > 0 else 0
            
            # Récupérer les barres pour calculer ATR
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M5, 0, 20)
            if rates is None or len(rates) < 14:
                # Fallback si pas de données
                return {
                    'price': price,
                    'atr': 0,
                    'spread': spread,
                    'trend': 'NEUTRAL',
                    'volatility': 0
                }
            
            # Calculer ATR (Average True Range)
            highs = np.array([r['high'] for r in rates])
            lows = np.array([r['low'] for r in rates])
            closes = np.array([r['close'] for r in rates])
            
            # True Range
            tr1 = highs[1:] - lows[1:]
            tr2 = np.abs(highs[1:] - closes[:-1])
            tr3 = np.abs(lows[1:] - closes[:-1])
            
            tr = np.maximum(tr1, np.maximum(tr2, tr3))
            atr = np.mean(tr[-14:]) if len(tr) >= 14 else np.mean(tr)
            
            # Calculer volatilité (ATR relatif au prix)
            volatility = (atr / price * 100) if price > 0 else 0
            
            # Déterminer la tendance simple
            if len(closes) >= 10:
                ma_fast = np.mean(closes[-5:])
                ma_slow = np.mean(closes[-10:])
                
                if ma_fast > ma_slow * 1.001:  # +0.1%
                    trend = 'BULLISH'
                elif ma_fast < ma_slow * 0.999:  # -0.1%
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
            print(f"Erreur get_market_info: {e}")
            return None
    
    # Attacher la méthode à l'instance Field
    import types
    field.get_market_info = types.MethodType(get_market_info, field)
    
    return field


def patch_hive_add_get_market_info_to_field(hive):
    """
    Patch le field de la Hive pour ajouter get_market_info()
    """
    if hasattr(hive, 'field') and hive.field is not None:
        hive.field = patch_field_add_get_market_info(hive.field)
        print("✅ get_market_info() ajouté à Field")
        
        # Test
        test_info = hive.field.get_market_info()
        if test_info:
            print(f"✅ Test get_market_info() OK: Prix={test_info['price']:.2f}, ATR={test_info['atr']:.2f}")
        else:
            print("⚠️  get_market_info() retourne None")
    else:
        print("❌ hive.field n'existe pas")
    
    return hive


if __name__ == '__main__':
    print("Patch Field.get_market_info()")
    print("\nUtilisation:")
    print("  from patch_field_get_market_info import patch_hive_add_get_market_info_to_field")
    print("  hive = patch_hive_add_get_market_info_to_field(hive)")
