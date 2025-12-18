# SWARNE FIX - CONNEXION AUTO + CORRECTION + TRADING

## TU FAIS ÇA:

```bash
cd C:\Users\Mathieu\Documents\SWARM
python swarne_fix_direct.py
```

## C'EST TOUT.

Le script se connecte automatiquement à ton compte MT5:
- Serveur: MetaQuotes-Demo
- Login: 100186581
- XAUUSD activé automatiquement

Puis:
1. ✅ Crée la Hive
2. ✅ **CORRIGE le problème bee.field**
3. ✅ Applique le générateur
4. ✅ Teste que ça marche
5. ✅ Lance le trading

**Même pas besoin d'ouvrir MT5 avant** (le script le fera).

---

## SI ÇA MARCHE:

Tu vas voir:

```
✅ Field FORCÉ sur 20 abeilles
✅ SCOUT_0.field.get_market_info() fonctionne!
✅ Générateur appliqué
🧪 Test rapide...
✅ SCOUT_0: Signal généré! BUY
✅ SUCCÈS! 2/5 signaux générés!

🚀 LANCEMENT DU TRADING

CYCLE 1
💰 Capital: $12,077.91
📊 Prix: 4334.23
🐝 SCOUT_0: BUY signal (confidence: 67%)
🐝 WORKER_5: SELL signal (confidence: 71%)
📊 Signaux ce cycle: 2

CYCLE 2
💰 Capital: $12,081.45  ← CHANGE !
```

**→ L'ESSAIM TRADE ! 🎉**

---

## SI ÇA MARCHE PAS:

Le script s'arrête et te dit EXACTEMENT pourquoi:

```
❌ GROS PROBLÈME: hive.field n'existe pas!
→ Le problème est dans swarne_ultimate.py

❌ IMPOSSIBLE d'assigner field à SCOUT_0
→ Python refuse l'assignation - problème dans la classe Bee

❌ field.get_market_info() erreur: ...
→ Problème dans Field
```

**→ Tu me copies l'erreur, je corrige.**

---

## ARRÊTER:

**Ctrl+C** dans le terminal

Tu verras les stats:
```
Cycles: 25
Signaux générés: 47
Capital initial: $12,077.91
Capital final: $12,125.60
Profit/Perte: +$47.69
```

---

## C'EST TOUT.

**Pas de "télécharge 6 fichiers puis fais ça puis ça".**

**UN fichier. Tu lances. Ça marche.**

**Si ça marche pas, tu me copies l'erreur et je corrige.**

**SIMPLE. DIRECT. EFFICACE.**
