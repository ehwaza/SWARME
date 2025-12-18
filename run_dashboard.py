#!/usr/bin/env python3
"""
🚀 SWARNE V2.0 - Launch Dashboard
Script de lancement du dashboard
"""

import sys
import logging
from dashboard_main import launch_dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Lancer le dashboard"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🐝 SWARNE V2.0 - DASHBOARD LAUNCH 🐝              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    logger.info("🚀 Launching SWARNE V2.0 Dashboard...")
    
    try:
        # TODO: Initialiser la Hive
        # from swarne.core.hive import Hive
        # hive = Hive(...)
        
        launch_dashboard(hive=None)
        
    except Exception as e:
        logger.error(f"❌ Error launching dashboard: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
