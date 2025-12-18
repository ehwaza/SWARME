"""
🎨 SWARNE V2.0 - Dashboard PyQt5
Interface graphique temps réel pour l'essaim
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QTextEdit,
                             QGroupBox, QGridLayout, QLCDNumber)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
import numpy as np


class SwarneDashboard(QMainWindow):
    """Dashboard principal SWARNE"""
    
    def __init__(self, hive=None):
        super().__init__()
        self.hive = hive
        self.equity_data = []
        self.time_data = []
        
        self.init_ui()
        
        # Timer pour mise à jour
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)  # Update every second
        
    def init_ui(self):
        """Initialiser l'interface"""
        self.setWindowTitle('🐝 SWARNE V2.0 - Hive Dashboard')
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
            }
            QPushButton:hover { background-color: #3a3a3a; }
        """)
        
    def create_top_bar(self):
        """Barre supérieure avec logo"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        title = QLabel('🐝 SWARNE V2.0 - HIVE DASHBOARD')
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setStyleSheet('color: #4CAF50;')
        
        layout.addWidget(title)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_metrics_panel(self):
        """Panel de métriques en temps réel"""
        group = QGroupBox('📊 Live Metrics')
        layout = QGridLayout()
        
        # Capital
        self.capital_lcd = QLCDNumber()
        self.capital_lcd.setDigitCount(10)
        self.capital_lcd.display(10000)
        self.capital_lcd.setStyleSheet('background-color: #2a2a2a; color: #4CAF50;')
        
        # Bees
        self.bees_lcd = QLCDNumber()
        self.bees_lcd.setDigitCount(3)
        self.bees_lcd.display(20)
        self.bees_lcd.setStyleSheet('background-color: #2a2a2a; color: #2196F3;')
        
        # Trades
        self.trades_lcd = QLCDNumber()
        self.trades_lcd.setDigitCount(5)
        self.trades_lcd.display(0)
        self.trades_lcd.setStyleSheet('background-color: #2a2a2a; color: #FF9800;')
        
        # P&L
        self.pnl_lcd = QLCDNumber()
        self.pnl_lcd.setDigitCount(8)
        self.pnl_lcd.display(0)
        self.pnl_lcd.setStyleSheet('background-color: #2a2a2a; color: #F44336;')
        
        layout.addWidget(QLabel('💰 Capital:'), 0, 0)
        layout.addWidget(self.capital_lcd, 0, 1)
        layout.addWidget(QLabel('🐝 Bees:'), 0, 2)
        layout.addWidget(self.bees_lcd, 0, 3)
        layout.addWidget(QLabel('📈 Trades:'), 0, 4)
        layout.addWidget(self.trades_lcd, 0, 5)
        layout.addWidget(QLabel('💵 P&L:'), 0, 6)
        layout.addWidget(self.pnl_lcd, 0, 7)
        
        group.setLayout(layout)
        return group
    
    def create_equity_chart(self):
        """Graphique d'equity en temps réel"""
        group = QGroupBox('📈 Equity Curve')
        layout = QVBoxLayout()
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#1e1e1e')
        self.plot_widget.setLabel('left', 'Capital ($)')
        self.plot_widget.setLabel('bottom', 'Time')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        self.equity_curve = self.plot_widget.plot(
            pen=pg.mkPen(color='#4CAF50', width=2)
        )
        
        layout.addWidget(self.plot_widget)
        group.setLayout(layout)
        return group
    
    def create_swarm_panel(self):
        """Panel de visualisation de l'essaim"""
        group = QGroupBox('🐝 Swarm Status')
        layout = QVBoxLayout()
        
        self.swarm_text = QTextEdit()
        self.swarm_text.setReadOnly(True)
        self.swarm_text.setStyleSheet('background-color: #2a2a2a; color: #e0e0e0;')
        self.swarm_text.setHtml('<b>Swarm Active</b>')
        
        layout.addWidget(self.swarm_text)
        group.setLayout(layout)
        return group
    
    def create_log_panel(self):
        """Panel de logs"""
        group = QGroupBox('📝 Activity Log')
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet('background-color: #2a2a2a; color: #e0e0e0;')
        
        layout.addWidget(self.log_text)
        group.setLayout(layout)
        return group
    
    def create_control_panel(self):
        """Panel de contrôle"""
        group = QGroupBox('🎮 Controls')
        layout = QVBoxLayout()
        
        self.start_btn = QPushButton('▶️ START')
        self.start_btn.clicked.connect(self.start_trading)
        self.start_btn.setStyleSheet('background-color: #4CAF50;')
        
        self.stop_btn = QPushButton('⏹️ STOP')
        self.stop_btn.clicked.connect(self.stop_trading)
        self.stop_btn.setStyleSheet('background-color: #F44336;')
        
        self.refresh_btn = QPushButton('🔄 REFRESH')
        self.refresh_btn.clicked.connect(self.refresh_display)
        
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.refresh_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def update_display(self):
        """Mise à jour de l'affichage"""
        if self.hive:
            # Update metrics
            self.capital_lcd.display(self.hive.guardian.current_capital)
            self.bees_lcd.display(len(self.hive.bees))
            
            # Update equity curve
            self.equity_data.append(self.hive.guardian.current_capital)
            self.time_data.append(len(self.equity_data))
            self.equity_curve.setData(self.time_data, self.equity_data)
    
    def add_log(self, message: str):
        """Ajouter un log"""
        self.log_text.append(message)
    
    def start_trading(self):
        """Démarrer le trading"""
        self.add_log('🚀 Trading started!')
    
    def stop_trading(self):
        """Arrêter le trading"""
        self.add_log('⏹️ Trading stopped!')
    
    def refresh_display(self):
        """Rafraîchir l'affichage"""
        self.add_log('🔄 Display refreshed!')


def launch_dashboard(hive=None):
    """Lancer le dashboard"""
    app = QApplication(sys.argv)
    dashboard = SwarneDashboard(hive)
    dashboard.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    launch_dashboard()
