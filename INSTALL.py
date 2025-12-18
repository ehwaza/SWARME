#!/usr/bin/env python3
"""
SWARNE - INSTALLATION AUTOMATIQUE
Remplace automatiquement les fichiers et lance le système
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║         SWARNE - INSTALLATION AUTOMATIQUE                    ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Dossier courant
    current_dir = Path(__file__).parent.absolute()
    print(f"📁 Dossier: {current_dir}")
    
    # Vérifier les fichiers
    files_to_install = [
        'swarne_ultimate.py',
        'bee_signal_generator.py',
        'quick_start.py'
    ]
    
    print("\n🔍 Vérification des fichiers...")
    for f in files_to_install:
        if not (current_dir / f).exists():
            print(f"❌ ERREUR: {f} introuvable !")
            print(f"   Assure-toi d'avoir extrait le ZIP !")
            input("\nAppuie sur Entrée pour quitter...")
            sys.exit(1)
        else:
            size = (current_dir / f).stat().st_size
            print(f"✅ {f} ({size:,} octets)")
    
    # Vérifier taille swarne_ultimate.py
    swarne_size = (current_dir / 'swarne_ultimate.py').stat().st_size
    swarne_lines = len((current_dir / 'swarne_ultimate.py').read_text(encoding='utf-8').splitlines())
    
    print(f"\n📊 swarne_ultimate.py: {swarne_lines} lignes")
    
    if swarne_lines < 900:
        print(f"⚠️  ATTENTION: Le fichier fait {swarne_lines} lignes !")
        print(f"   Il devrait faire 960 lignes !")
        print(f"   Le fichier est peut-être corrompu !")
        response = input("\nContinuer quand même ? (oui/non): ")
        if response.lower() != 'oui':
            sys.exit(1)
    
    # Tout est OK
    print("\n✅ TOUS LES FICHIERS SONT PRÊTS !")
    print("\n" + "="*60)
    print("Le système va maintenant:")
    print("  1. Vérifier les fichiers")
    print("  2. Lancer quick_start.py")
    print("  3. Mode 9 → xauusd → 20 abeilles")
    print("="*60)
    
    input("\nAppuie sur Entrée pour lancer...")
    
    # Lancer quick_start.py
    print("\n🚀 LANCEMENT DE QUICK_START.PY...\n")
    os.system(f'python "{current_dir / "quick_start.py"}"')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Installation annulée")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        input("\nAppuie sur Entrée pour quitter...")
        sys.exit(1)
