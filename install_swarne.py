"""
Installation automatique SWARNE - Avec vérification

Ce script installe et vérifie que les corrections sont bien appliquées
"""

import os
import sys
import hashlib

print("\n" + "="*70)
print("🔧 INSTALLATION SWARNE - PACKAGE CORRIGÉ")
print("="*70 + "\n")

# Vérifier que les fichiers FIXED existent
if not os.path.exists("swarne_ultimate_FIXED.py"):
    print("❌ swarne_ultimate_FIXED.py non trouvé!")
    print("   Extrais bien le ZIP SWARNE_PACKAGE_FINAL.zip")
    input("\nAppuie sur Entrée...")
    sys.exit(1)

if not os.path.exists("bee_signal_generator_FIXED.py"):
    print("❌ bee_signal_generator_FIXED.py non trouvé!")
    print("   Extrais bien le ZIP SWARNE_PACKAGE_FINAL.zip")
    input("\nAppuie sur Entrée...")
    sys.exit(1)

# Vérifier la taille des fichiers FIXED (pour être sûr qu'ils sont corrects)
size_swarne = os.path.getsize("swarne_ultimate_FIXED.py")
size_generator = os.path.getsize("bee_signal_generator_FIXED.py")

print(f"📦 Fichiers trouvés:")
print(f"   swarne_ultimate_FIXED.py: {size_swarne} octets")
print(f"   bee_signal_generator_FIXED.py: {size_generator} octets\n")

# Vérifier que les fichiers FIXED sont différents des originaux
if size_swarne < 32000:
    print("❌ ERREUR: swarne_ultimate_FIXED.py est trop petit!")
    print("   Il devrait faire ~34000 octets (avec corrections)")
    print(f"   Actuellement: {size_swarne} octets")
    print("\n   Le fichier FIXED n'est pas le bon!")
    input("\nAppuie sur Entrée...")
    sys.exit(1)

print("✅ Fichiers FIXED ont la bonne taille\n")

# Vérifier que les corrections sont présentes
print("🔍 Vérification des corrections...")

with open("swarne_ultimate_FIXED.py", "r", encoding="utf-8") as f:
    content = f.read()
    
    corrections_found = 0
    
    if "CORRECTION: Donner field à toutes les abeilles" in content:
        print("   ✅ Correction 1: bee.field assigné")
        corrections_found += 1
    else:
        print("   ❌ Correction 1 manquante!")
    
    if "def get_market_info(self):" in content:
        print("   ✅ Correction 2: get_market_info() présent")
        corrections_found += 1
    else:
        print("   ❌ Correction 2 manquante!")
    
    if "Garder au moins 50% des abeilles" in content or "cutoff = len(self.bees) // 2" in content:
        print("   ✅ Correction 3: evolve() corrigé")
        corrections_found += 1
    else:
        print("   ❌ Correction 3 manquante!")

if corrections_found < 3:
    print(f"\n❌ PROBLÈME: Seulement {corrections_found}/3 corrections trouvées!")
    print("   Les fichiers FIXED ne sont pas corrects!")
    input("\nAppuie sur Entrée...")
    sys.exit(1)

print(f"\n✅ TOUTES LES CORRECTIONS PRÉSENTES ({corrections_found}/3)\n")

# Backup des anciens fichiers
print("💾 Sauvegarde des anciens fichiers...")

if os.path.exists("swarne_ultimate.py"):
    if not os.path.exists("swarne_ultimate_OLD.py"):
        os.rename("swarne_ultimate.py", "swarne_ultimate_OLD.py")
        print("   ✅ swarne_ultimate.py → swarne_ultimate_OLD.py")
    else:
        print("   ⚠️  swarne_ultimate_OLD.py existe déjà (pas de backup)")

if os.path.exists("bee_signal_generator.py"):
    if not os.path.exists("bee_signal_generator_OLD.py"):
        os.rename("bee_signal_generator.py", "bee_signal_generator_OLD.py")
        print("   ✅ bee_signal_generator.py → bee_signal_generator_OLD.py")
    else:
        print("   ⚠️  bee_signal_generator_OLD.py existe déjà (pas de backup)")

print()

# Installation
print("📥 Installation des fichiers corrigés...")

import shutil

shutil.copy("swarne_ultimate_FIXED.py", "swarne_ultimate.py")
print("   ✅ swarne_ultimate_FIXED.py → swarne_ultimate.py")

shutil.copy("bee_signal_generator_FIXED.py", "bee_signal_generator.py")
print("   ✅ bee_signal_generator_FIXED.py → bee_signal_generator.py")

print()

# Vérification finale
print("🔍 Vérification finale...")

final_size_swarne = os.path.getsize("swarne_ultimate.py")
final_size_generator = os.path.getsize("bee_signal_generator.py")

if final_size_swarne == size_swarne:
    print(f"   ✅ swarne_ultimate.py: {final_size_swarne} octets (OK)")
else:
    print(f"   ❌ ERREUR: Tailles différentes!")

if final_size_generator == size_generator:
    print(f"   ✅ bee_signal_generator.py: {final_size_generator} octets (OK)")
else:
    print(f"   ❌ ERREUR: Tailles différentes!")

print("\n" + "="*70)
print("✅ INSTALLATION TERMINÉE")
print("="*70)

print("\nFichiers installés:")
print("  ✅ swarne_ultimate.py (corrigé)")
print("  ✅ bee_signal_generator.py (corrigé)")
print("\nBackups créés:")
print("  📁 swarne_ultimate_OLD.py")
print("  📁 bee_signal_generator_OLD.py")
print("\nMaintenant lance:")
print("  python quick_start.py")
print("  Choisis mode 9 (Production Unifié)")
print("\n💰 L'essaim va TRADER avec les corrections !")

input("\nAppuie sur Entrée pour terminer...")
