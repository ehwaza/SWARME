"""
PATCH DÉFINITIF - Force run_cycle() à VRAIMENT trader

Ce patch remplace run_cycle() pour:
1. Générer les signaux
2. Les valider avec Guardian
3. Les exécuter avec Coordinator
4. Mettre à jour les fitness

Sans ce patch, les signaux sont générés mais jamais exécutés.
"""

def patch_hive_force_trading_cycle(hive):
    """
    Remplace run_cycle() pour forcer l'exécution des trades
    """
    
    original_run_cycle = hive.run_cycle
    
    def run_cycle_with_forced_trading(self):
        """
        Cycle qui FORCE la génération et l'exécution des signaux
        """
        
        cycle_signals = 0
        cycle_trades = 0
        
        print(f"\n{'='*70}")
        print(f"🔄 CYCLE FORCÉ - Génération et exécution active")
        print(f"{'='*70}")
        
        # Pour chaque abeille
        for bee in self.bees:
            
            # 1. GÉNÉRER le signal
            if hasattr(bee, 'generate_signal'):
                try:
                    signal = bee.generate_signal()
                    
                    if signal:
                        cycle_signals += 1
                        signal_type = signal.get('type', 'N/A')
                        confidence = signal.get('confidence', 0)
                        
                        print(f"🐝 {bee.bee_id}: {signal_type} signal (confidence: {confidence}%)")
                        
                        # 2. VALIDER avec Guardian
                        if hasattr(self, 'guardian') and hasattr(self.guardian, 'validate_signal'):
                            try:
                                validated = self.guardian.validate_signal(signal, bee)
                                
                                if validated:
                                    print(f"   ✅ Guardian validated")
                                    
                                    # 3. EXÉCUTER avec Coordinator
                                    if hasattr(self, 'coordinator'):
                                        try:
                                            # Préparer l'ordre
                                            trade_params = {
                                                'symbol': self.field.symbol if hasattr(self, 'field') else 'XAUUSD',
                                                'type': signal_type,
                                                'volume': signal.get('volume', 0.01),
                                                'price': signal.get('price', 0),
                                                'sl': signal.get('sl', 0),
                                                'tp': signal.get('tp', 0)
                                            }
                                            
                                            # Exécuter
                                            result = self.coordinator.execute_trade(trade_params)
                                            
                                            if result and result.get('success'):
                                                cycle_trades += 1
                                                print(f"   ✅ Trade executed: Order #{result.get('order_id', 'N/A')}")
                                                
                                                # Mettre à jour fitness
                                                if hasattr(bee, 'fitness'):
                                                    bee.fitness += 1
                                            else:
                                                print(f"   ❌ Trade failed: {result.get('error', 'Unknown')}")
                                        
                                        except Exception as e:
                                            print(f"   ❌ Coordinator error: {e}")
                                    else:
                                        print(f"   ⚠️  No coordinator available")
                                else:
                                    print(f"   ❌ Guardian rejected signal")
                            
                            except Exception as e:
                                print(f"   ❌ Guardian error: {e}")
                        else:
                            print(f"   ⚠️  No guardian available")
                
                except Exception as e:
                    print(f"❌ {bee.bee_id}: Error generating signal - {e}")
        
        print(f"\n📊 Cycle summary:")
        print(f"   Signals generated: {cycle_signals}")
        print(f"   Trades executed: {cycle_trades}")
        print(f"{'='*70}\n")
        
        # Appeler le cycle original pour les autres trucs (metrics, etc.)
        try:
            return original_run_cycle()
        except:
            pass
    
    # Remplacer run_cycle
    import types
    hive.run_cycle = types.MethodType(run_cycle_with_forced_trading, hive)
    
    print("✅ run_cycle() patché avec exécution forcée des trades")
    
    return hive


if __name__ == '__main__':
    print("Patch run_cycle() - Force trading execution")
    print("\nUtilisation:")
    print("  from patch_force_trading_cycle import patch_hive_force_trading_cycle")
    print("  hive = patch_hive_force_trading_cycle(hive)")
