"""
🎨 SWARNE V2.0 - Dashboard Intégré avec Live Trading
Interface graphique temps réel avec contrôle complet de l'essaim
"""

import sys
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QTextEdit,
                             QGroupBox, QGridLayout, QLCDNumber, QMessageBox)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import pyqtgraph as pg
import numpy as np

# Import SWARNE components
try:
    from swarne_ultimate import Hive, Field, Guardian
    SWARNE_AVAILABLE = True
except:
    SWARNE_AVAILABLE = False
    print("⚠️  swarne_ultimate.py non trouvé, mode démo activé")


class TradingThread(QThread):
    """Thread pour le trading en arrière-plan"""
    
    # Signaux pour communication avec l'interface
    cycle_completed = pyqtSignal(int)  # Numéro du cycle
    trade_signal = pyqtSignal(str)  # Signal de trade
    error_signal = pyqtSignal(str)  # Erreur
    metrics_updated = pyqtSignal(dict)  # Métriques mises à jour
    
    def __init__(self, hive):
        super().__init__()
        self.hive = hive
        self.running = False
        self.cycle_count = 0
        
    def run(self):
        """Boucle de trading principale"""
        self.running = True
        self.cycle_count = 0
        
        try:
            while self.running:
                # Exécuter un cycle
                self.hive.run_cycle()
                self.cycle_count += 1
                
                # Émettre le signal de cycle complété
                self.cycle_completed.emit(self.cycle_count)
                
                # Récupérer et émettre les métriques
                metrics = self.get_current_metrics()
                self.metrics_updated.emit(metrics)
                
                # Pause entre les cycles (4 secondes)
                time.sleep(4)
                
        except Exception as e:
            self.error_signal.emit(f"Erreur trading: {str(e)}")
            self.running = False
    
    def stop(self):
        """Arrêter le trading"""
        self.running = False
        
    def get_current_metrics(self):
        """Récupérer les métriques actuelles de la Hive"""
        try:
            capital = float(self.hive.guardian.capital)
            active_bees = len([b for b in self.hive.bees if b.fitness > 0])
            total_trades = len(self.hive.trade_history) if hasattr(self.hive, 'trade_history') else 0
            
            # Calculer P&L
            initial_capital = float(self.hive.guardian.initial_capital) if hasattr(self.hive.guardian, 'initial_capital') else 10000.0
            pnl = capital - initial_capital
            pnl_percent = (pnl / initial_capital) * 100 if initial_capital > 0 else 0
            
            return {
                'capital': capital,
                'active_bees': active_bees,
                'total_bees': len(self.hive.bees),
                'trades': total_trades,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'cycle': self.cycle_count
            }
        except:
            return {
                'capital': 10000,
                'active_bees': 0,
                'total_bees': 20,
                'trades': 0,
                'pnl': 0,
                'pnl_percent': 0,
                'cycle': self.cycle_count
            }


class SwarneDashboard(QMainWindow):
    """Dashboard principal SWARNE avec Live Trading intégré"""
    
    def __init__(self, hive=None, symbol='EURUSD', capital=10000):
        super().__init__()
        self.hive = hive
        self.symbol = symbol
        self.initial_capital = capital
        self.trading_thread = None
        self.trading_active = False
        
        # Données pour graphiques
        self.equity_data = [capital]
        self.time_data = [0]
        self.cycle_count = 0
        
        self.init_ui()
        
        # Timer pour mise à jour de l'affichage
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(1000)  # Mise à jour chaque seconde
        
    def init_ui(self):
        """Initialiser l'interface"""
        self.setWindowTitle(f'🐝 SWARNE V2.0 - Live Dashboard - {self.symbol}')
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Top bar
        main_layout.addWidget(self.create_top_bar())
        
        # Metrics panel
        main_layout.addWidget(self.create_metrics_panel())
        
        # Middle section (Chart + Swarm)
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.create_equity_chart(), 2)
        middle_layout.addWidget(self.create_swarm_panel(), 1)
        main_layout.addLayout(middle_layout)
        
        # Bottom section (Logs + Controls)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.create_log_panel(), 2)
        bottom_layout.addWidget(self.create_control_panel(), 1)
        main_layout.addLayout(bottom_layout)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QGroupBox { 
                color: #e0e0e0; 
                border: 2px solid #3a3a3a;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QLabel { color: #e0e0e0; }
            QPushButton {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #3a3a3a; }
            QLCDNumber {
                background-color: #0a0a0a;
                color: #4CAF50;
                border: 1px solid #3a3a3a;
            }
        """)
        
    def create_top_bar(self):
        """Barre supérieure avec titre"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        title = QLabel('🐝 SWARNE V2.0 - LIVE TRADING DASHBOARD')
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setStyleSheet('color: #4CAF50;')
        
        # Status indicator
        self.status_label = QLabel('⚫ Stopped')
        self.status_label.setFont(QFont('Arial', 12))
        self.status_label.setStyleSheet('color: #ff4444;')
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.status_label)
        
        widget.setLayout(layout)
        return widget
    
    def create_metrics_panel(self):
        """Panel de métriques en temps réel"""
        group = QGroupBox('📊 Live Metrics')
        layout = QGridLayout()
        
        # Capital
        layout.addWidget(QLabel('💰 Capital:'), 0, 0)
        self.capital_lcd = QLCDNumber()
        self.capital_lcd.setDigitCount(8)
        self.capital_lcd.display(self.initial_capital)
        self.capital_lcd.setMinimumHeight(50)
        layout.addWidget(self.capital_lcd, 0, 1)
        
        # Bees
        layout.addWidget(QLabel('🐝 Bees:'), 0, 2)
        self.bees_lcd = QLCDNumber()
        self.bees_lcd.setDigitCount(3)
        self.bees_lcd.display(20)
        self.bees_lcd.setMinimumHeight(50)
        layout.addWidget(self.bees_lcd, 0, 3)
        
        # Trades
        layout.addWidget(QLabel('📈 Trades:'), 1, 0)
        self.trades_lcd = QLCDNumber()
        self.trades_lcd.setDigitCount(5)
        self.trades_lcd.display(0)
        self.trades_lcd.setMinimumHeight(50)
        layout.addWidget(self.trades_lcd, 1, 1)
        
        # P&L
        layout.addWidget(QLabel('💵 P&L:'), 1, 2)
        self.pnl_lcd = QLCDNumber()
        self.pnl_lcd.setDigitCount(6)
        self.pnl_lcd.display(0)
        self.pnl_lcd.setMinimumHeight(50)
        layout.addWidget(self.pnl_lcd, 1, 3)
        
        group.setLayout(layout)
        return group
    
    def create_equity_chart(self):
        """Graphique d'equity curve"""
        group = QGroupBox('📈 Equity Curve')
        layout = QVBoxLayout()
        
        # PyQtGraph pour graphique
        pg.setConfigOption('background', '#0a0a0a')
        pg.setConfigOption('foreground', '#4CAF50')
        
        self.equity_plot = pg.PlotWidget()
        self.equity_plot.setLabel('left', 'Capital ($)')
        self.equity_plot.setLabel('bottom', 'Time (cycles)')
        self.equity_plot.showGrid(x=True, y=True, alpha=0.3)
        
        # Ligne d'equity
        self.equity_curve = self.equity_plot.plot(
            self.time_data, 
            self.equity_data, 
            pen=pg.mkPen(color='#4CAF50', width=2)
        )
        
        layout.addWidget(self.equity_plot)
        group.setLayout(layout)
        return group
    
    def create_swarm_panel(self):
        """Panel d'état de l'essaim"""
        group = QGroupBox('🐝 Swarm Status')
        layout = QVBoxLayout()
        
        self.swarm_text = QTextEdit()
        self.swarm_text.setReadOnly(True)
        self.swarm_text.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #4CAF50;
                border: 1px solid #3a3a3a;
                font-family: 'Courier New';
                font-size: 10pt;
            }
        """)
        self.swarm_text.setPlainText("Swarm Active\n\n⏳ Waiting for trading to start...")
        
        layout.addWidget(self.swarm_text)
        group.setLayout(layout)
        return group
    
    def create_log_panel(self):
        """Panel de logs d'activité"""
        group = QGroupBox('📝 Activity Log')
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                font-family: 'Courier New';
                font-size: 9pt;
            }
        """)
        
        # Logs initiaux
        self.log("✅ Dashboard initialized")
        self.log(f"📊 Symbol: {self.symbol}")
        self.log(f"💰 Initial Capital: ${self.initial_capital:,.2f}")
        
        layout.addWidget(self.log_text)
        group.setLayout(layout)
        return group
    
    def create_control_panel(self):
        """Panel de contrôles"""
        group = QGroupBox('🎮 Controls')
        layout = QVBoxLayout()
        
        # Bouton START
        self.start_btn = QPushButton('▶ START')
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                padding: 15px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #388e3c; }
            QPushButton:disabled { background-color: #1b5e20; color: #666; }
        """)
        self.start_btn.clicked.connect(self.on_start)
        layout.addWidget(self.start_btn)
        
        # Bouton STOP
        self.stop_btn = QPushButton('⏸ STOP')
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #c62828;
                color: white;
                padding: 15px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #d32f2f; }
            QPushButton:disabled { background-color: #b71c1c; color: #666; }
        """)
        self.stop_btn.clicked.connect(self.on_stop)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        # Bouton REFRESH
        self.refresh_btn = QPushButton('🔄 REFRESH')
        self.refresh_btn.clicked.connect(self.on_refresh)
        layout.addWidget(self.refresh_btn)
        
        layout.addStretch()
        
        # Info panel
        info_label = QLabel(
            f"Symbol: {self.symbol}\n"
            f"Capital: ${self.initial_capital:,.0f}\n"
            f"Bees: {len(self.hive.bees) if self.hive else 20}"
        )
        info_label.setStyleSheet("color: #999; font-size: 9pt;")
        layout.addWidget(info_label)
        
        group.setLayout(layout)
        return group
    
    def on_start(self):
        """Démarrer le trading"""
        if not self.hive:
            QMessageBox.warning(self, "Error", "No Hive initialized!")
            return
        
        if self.trading_active:
            return
        
        # Confirmer avec l'utilisateur
        reply = QMessageBox.question(
            self,
            'Start Trading',
            f'Start live trading on {self.symbol}?\n\n'
            f'Capital: ${self.initial_capital:,.2f}\n'
            f'Bees: {len(self.hive.bees)}\n\n'
            '⚠️ Make sure you are in DEMO account!',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Démarrer le thread de trading
        self.trading_thread = TradingThread(self.hive)
        self.trading_thread.cycle_completed.connect(self.on_cycle_completed)
        self.trading_thread.trade_signal.connect(self.on_trade_signal)
        self.trading_thread.error_signal.connect(self.on_error)
        self.trading_thread.metrics_updated.connect(self.on_metrics_updated)
        self.trading_thread.start()
        
        self.trading_active = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText('🟢 Trading Active')
        self.status_label.setStyleSheet('color: #4CAF50;')
        
        self.log("🚀 Trading started!")
        self.log("⏳ Running trading cycles...")
        
    def on_stop(self):
        """Arrêter le trading"""
        if not self.trading_active or not self.trading_thread:
            return
        
        self.log("🛑 Stopping trading...")
        self.trading_thread.stop()
        self.trading_thread.wait()  # Attendre la fin du thread
        
        self.trading_active = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText('⚫ Stopped')
        self.status_label.setStyleSheet('color: #ff4444;')
        
        self.log("✅ Trading stopped!")
        
    def on_refresh(self):
        """Rafraîchir l'affichage"""
        self.log("🔄 Display refreshed!")
        self.update_display()
        
    def on_cycle_completed(self, cycle_num):
        """Callback quand un cycle est complété"""
        self.cycle_count = cycle_num
        self.log(f"✅ Cycle {cycle_num} completed")
        
    def on_trade_signal(self, signal_text):
        """Callback pour les signaux de trade"""
        self.log(f"📊 {signal_text}")
        
    def on_error(self, error_msg):
        """Callback pour les erreurs"""
        self.log(f"❌ ERROR: {error_msg}")
        QMessageBox.critical(self, "Trading Error", error_msg)
        self.on_stop()
        
    def on_metrics_updated(self, metrics):
        """Callback quand les métriques sont mises à jour"""
        # Mettre à jour les LCDs
        self.capital_lcd.display(int(metrics['capital']))
        self.bees_lcd.display(metrics['active_bees'])
        self.trades_lcd.display(metrics['trades'])
        self.pnl_lcd.display(int(metrics['pnl']))
        
        # Mettre à jour le graphique
        self.time_data.append(metrics['cycle'])
        self.equity_data.append(metrics['capital'])
        self.equity_curve.setData(self.time_data, self.equity_data)
        
        # Mettre à jour le panel swarm
        swarm_status = f"""🐝 SWARM STATUS

Cycle: {metrics['cycle']}
Active Bees: {metrics['active_bees']}/{metrics['total_bees']}
Total Trades: {metrics['trades']}

Capital: ${metrics['capital']:,.2f}
P&L: ${metrics['pnl']:,.2f} ({metrics['pnl_percent']:.2f}%)

Status: {'🟢 Active' if self.trading_active else '⚫ Stopped'}
"""
        self.swarm_text.setPlainText(swarm_status)
        
    def update_display(self):
        """Mise à jour périodique de l'affichage"""
        # Afficher l'heure actuelle
        current_time = datetime.now().strftime("%H:%M:%S")
        # Cette fonction tourne en arrière-plan toutes les secondes
        
    def log(self, message):
        """Ajouter un message au log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll vers le bas
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("🐝 SWARNE V2.0 - Dashboard Intégré")
    print("="*60 + "\n")
    
    # Créer l'application
    app = QApplication(sys.argv)
    
    # Paramètres
    SYMBOL = 'EURUSD'
    CAPITAL = 10000
    NUM_BEES = 20
    
    # Créer la Hive
    hive = None
    if SWARNE_AVAILABLE:
        print("🔧 Initialisation de la Hive...")
        try:
            guardian = Guardian(capital=CAPITAL)
            field = Field(symbol=SYMBOL)
            hive = Hive(guardian=guardian, field=field, num_bees=NUM_BEES)
            print(f"✅ Hive créée: {NUM_BEES} abeilles, ${CAPITAL:,.0f}\n")
            
            # ====================================
            # PATCH: Activer les abeilles !
            # ====================================
            print("🔧 Application du patch 'Abeilles Actives'...")
            try:
                from patch_active_bees import patch_hive_for_active_trading
                hive = patch_hive_for_active_trading(hive)
                print("✅ Patch appliqué: Abeilles activées !\n")
            except ImportError:
                print("⚠️  patch_active_bees.py non trouvé")
                print("   Les abeilles utiliseront la logique standard\n")
            # ====================================
            
        except Exception as e:
            print(f"❌ Erreur création Hive: {e}")
            print("⚠️  Mode démo activé\n")
    
    # Créer et afficher le dashboard
    dashboard = SwarneDashboard(hive=hive, symbol=SYMBOL, capital=CAPITAL)
    dashboard.show()
    
    print("🎨 Dashboard lancé !")
    print("💡 Cliquez sur START pour démarrer le trading\n")
    
    # Lancer l'application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
