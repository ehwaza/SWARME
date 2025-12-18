"""
🔧 SWARNE - Patch Field Access
Donne accès au Field à toutes les abeilles

Ce patch résout le problème : bee.field n'existe pas
"""

import logging

logger = logging.getLogger('SWARNE.FieldPatch')


def patch_hive_give_field_to_bees(hive):
    """
    Donner accès au Field à toutes les abeilles
    
    Le problème: les abeilles n'ont pas d'attribut 'field'
    La solution: donner le field de la Hive à chaque abeille
    """
    
    logger.info("🔧 Giving field access to all bees...")
    
    # Vérifier que la Hive a un field
    if not hasattr(hive, 'field'):
        logger.error("❌ Hive does not have a field!")
        return hive
    
    # Donner le field à chaque abeille
    patched_count = 0
    for bee in hive.bees:
        if not hasattr(bee, 'field') or bee.field is None:
            bee.field = hive.field
            patched_count += 1
            logger.debug(f"✅ {bee.bee_id} given field access")
    
    logger.info(f"✅ {patched_count} bees given field access")
    
    # Patcher evolve() pour donner field aux nouvelles abeilles
    if hasattr(hive, 'evolve'):
        original_evolve = hive.evolve
        
        def evolve_with_field_patch(self):
            """Evolve avec field automatiquement donné aux nouvelles abeilles"""
            
            # Compter les abeilles avant
            bees_before = len(self.bees)
            
            # Appeler evolve original
            result = original_evolve()
            
            # Compter les abeilles après
            bees_after = len(self.bees)
            
            # Si nouvelles abeilles créées
            if bees_after > bees_before:
                new_bees_count = bees_after - bees_before
                logger.info(f"🐣 {new_bees_count} new bees detected, giving field access...")
                
                # Donner field aux nouvelles abeilles
                patched = 0
                for bee in self.bees:
                    if not hasattr(bee, 'field') or bee.field is None:
                        bee.field = self.field
                        patched += 1
                
                if patched > 0:
                    logger.info(f"✅ {patched} new bees given field access")
            
            return result
        
        hive.evolve = evolve_with_field_patch.__get__(hive, hive.__class__)
        logger.info("✅ evolve() patched with auto field assignment")
    
    logger.info("✅ Field access patch fully applied")
    
    return hive


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔧 SWARNE - Patch Field Access")
    print("="*60 + "\n")
    
    print("Ce patch donne accès au Field à toutes les abeilles.")
    print("\nUtilisation:")
    print("  from patch_field_access import patch_hive_give_field_to_bees")
    print("  hive = patch_hive_give_field_to_bees(hive)")
    print("\n")
