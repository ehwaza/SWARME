"""
🔌 SWARNE - Connecteur MT5 Réel
Connecte le Guardian au compte MT5 réel et exécute de vrais trades
"""

import MetaTrader5 as mt5
import logging
from datetime import datetime

logger = logging.getLogger('SWARNE.MT5Connector')


class MT5Connector:
    """
    Connecteur pour trading réel sur MT5
    Gère la connexion, le capital réel et l'exécution des trades
    """
    
    def __init__(self, symbol='EURUSD'):
        self.symbol = symbol
        self.connected = False
        self.account_info = None
        self.real_capital = 0.0
        
    def connect(self):
        """Connecter au compte MT5"""
        logger.info("🔌 Connecting to MetaTrader 5...")
        
        if not mt5.initialize():
            logger.error("❌ Failed to initialize MT5")
            return False
        
        # Récupérer infos du compte
        self.account_info = mt5.account_info()
        if self.account_info is None:
            logger.error("❌ Failed to get account info")
            mt5.shutdown()
            return False
        
        self.real_capital = float(self.account_info.balance)
        self.connected = True
        
        logger.info(f"✅ Connected to MT5")
        logger.info(f"   Account: {self.account_info.login}")
        logger.info(f"   Type: {'DEMO' if self.account_info.trade_mode == 0 else 'REAL'}")
        logger.info(f"   Balance: ${self.real_capital:,.2f}")
        logger.info(f"   Server: {self.account_info.server}")
        
        # Vérifier le symbole
        if not self._verify_symbol():
            logger.error(f"❌ Symbol {self.symbol} not available")
            mt5.shutdown()
            return False
        
        return True
    
    def _verify_symbol(self):
        """Vérifier que le symbole est disponible"""
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            return False
        
        # Sélectionner le symbole
        if not mt5.symbol_select(self.symbol, True):
            return False
        
        logger.info(f"✅ Symbol {self.symbol} verified and selected")
        return True
    
    def get_real_capital(self):
        """Récupérer le capital réel du compte MT5"""
        if not self.connected:
            return None
        
        # Rafraîchir les infos
        self.account_info = mt5.account_info()
        if self.account_info:
            self.real_capital = float(self.account_info.balance)
            return self.real_capital
        
        return None
    
    def execute_trade(self, signal):
        """
        Exécuter un trade RÉEL sur MT5
        
        Args:
            signal: Dict avec type, entry_price, stop_loss, take_profit
            
        Returns:
            Dict avec résultat du trade
        """
        if not self.connected:
            logger.error("❌ Not connected to MT5")
            return None
        
        try:
            # Déterminer le type d'ordre
            if signal['type'] == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(self.symbol).ask
            elif signal['type'] == 'SELL':
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(self.symbol).bid
            else:
                logger.warning(f"⚠️  Invalid signal type: {signal['type']}")
                return None
            
            # Calculer le volume (lot size)
            # 1% du capital par trade
            risk_percent = 0.01
            symbol_info = mt5.symbol_info(self.symbol)
            
            # Volume basé sur le capital
            capital = self.get_real_capital()
            if capital is None:
                capital = self.real_capital
            
            # Calcul simple: 0.01 lot par $1000 de capital
            volume = max(0.01, round((capital / 1000) * 0.01, 2))
            
            # S'assurer que le volume est dans les limites
            volume = max(symbol_info.volume_min, min(volume, symbol_info.volume_max))
            
            # Préparer la requête
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": "SWARNE Trade",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Ajouter SL/TP si disponibles
            if signal.get('stop_loss'):
                request['sl'] = signal['stop_loss']
            if signal.get('take_profit'):
                request['tp'] = signal['take_profit']
            
            # Envoyer l'ordre
            logger.info(f"📤 Sending order: {signal['type']} {volume} {self.symbol} @ {price}")
            result = mt5.order_send(request)
            
            if result is None:
                logger.error("❌ Order send failed: No result")
                return None
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"❌ Order failed: {result.retcode} - {result.comment}")
                return None
            
            # Succès !
            logger.info(f"✅ Trade executed: {signal['type']} {volume} @ {result.price}")
            logger.info(f"   Order: {result.order}")
            logger.info(f"   Deal: {result.deal}")
            
            return {
                'success': True,
                'order': result.order,
                'deal': result.deal,
                'volume': volume,
                'price': result.price,
                'type': signal['type'],
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"❌ Trade execution error: {e}")
            return None
    
    def get_open_positions(self):
        """Récupérer les positions ouvertes"""
        if not self.connected:
            return []
        
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None:
            return []
        
        return list(positions)
    
    def close_position(self, position):
        """Fermer une position"""
        if not self.connected:
            return False
        
        try:
            # Déterminer le type d'ordre de fermeture
            if position.type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(self.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(self.symbol).ask
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": position.ticket,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": "SWARNE Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Position closed: {position.ticket}")
                return True
            else:
                logger.error(f"❌ Failed to close position: {result.comment if result else 'Unknown error'}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Close position error: {e}")
            return False
    
    def disconnect(self):
        """Déconnecter de MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("🔌 Disconnected from MT5")


def patch_guardian_with_mt5_connector(guardian, connector):
    """
    Patcher le Guardian pour utiliser le capital réel MT5
    """
    
    logger.info("🔧 Patching Guardian with MT5 connector...")
    
    # 1. Mettre à jour le capital avec le capital réel
    real_capital = connector.get_real_capital()
    if real_capital:
        guardian.capital = real_capital
        guardian.initial_capital = real_capital
        logger.info(f"✅ Guardian capital updated: ${real_capital:,.2f}")
    
    # 2. Attacher le connecteur au Guardian
    guardian.mt5_connector = connector
    
    # 3. Patcher la méthode execute_trade
    original_execute = guardian.execute_trade if hasattr(guardian, 'execute_trade') else None
    
    def patched_execute_trade(signal):
        """Version patchée qui exécute sur MT5"""
        
        logger.info(f"🎯 Executing trade via MT5: {signal['type']}")
        
        # Exécuter sur MT5 réel
        result = connector.execute_trade(signal)
        
        if result and result['success']:
            # Mettre à jour le capital du Guardian
            new_capital = connector.get_real_capital()
            if new_capital:
                guardian.capital = new_capital
            
            return result
        
        return None
    
    guardian.execute_trade = patched_execute_trade
    
    logger.info("✅ Guardian patched with MT5 connector")


def initialize_mt5_system(symbol='EURUSD'):
    """
    Initialiser le système complet avec connexion MT5 réelle
    
    Returns:
        (connector, real_capital) ou (None, None) si échec
    """
    
    print("\n" + "="*60)
    print("🔌 INITIALISATION CONNEXION MT5 RÉELLE")
    print("="*60 + "\n")
    
    # Créer le connecteur
    connector = MT5Connector(symbol=symbol)
    
    # Connecter
    if not connector.connect():
        print("❌ Échec de connexion à MT5")
        print("   → Vérifiez que MT5 est ouvert")
        print("   → Vérifiez votre connexion\n")
        return None, None
    
    # Récupérer le capital réel
    real_capital = connector.get_real_capital()
    
    print(f"\n✅ Connexion MT5 établie")
    print(f"   Capital réel: ${real_capital:,.2f}")
    print(f"   Symbole: {symbol}\n")
    
    return connector, real_capital


if __name__ == '__main__':
    # Test du connecteur
    connector, capital = initialize_mt5_system('EURUSD')
    
    if connector:
        print(f"✅ Test réussi !")
        print(f"   Capital: ${capital:,.2f}")
        
        # Test positions
        positions = connector.get_open_positions()
        print(f"   Positions ouvertes: {len(positions)}")
        
        connector.disconnect()
