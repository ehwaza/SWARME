"""
🚀 SWARNE V2.0 - Lanceur Dashboard Live Trading
Script simplifié pour démarrer le dashboard intégré
"""

import sys
from dashboard_live_integrated import main

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║  🐝 SWARNE V2.0 - DASHBOARD LIVE TRADING 🐝                 ║
║                                                              ║
║  Interface graphique avec contrôle complet de l'essaim      ║
║  Métriques temps réel • Equity curve • Trading live         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard fermé proprement")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        input("\nAppuyez sur Entrée pour quitter...")
