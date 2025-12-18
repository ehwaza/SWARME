# 🛡️ ALGIZ.mq5 - GUIDE DE RÉPARATION COMPLÈTE

## 📊 ANALYSE DES ERREURS

Vos erreurs proviennent de **constantes non déclarées** pour les objets graphiques MQL5.

### Erreurs Identifiées (24 erreurs)
- **Lignes 386, 402, 423** : `ObjectCreate()` - Type d'objet invalide
- **Lignes 396-397, 412-413, 433-434** : `ObjectSetInteger()` - Propriété invalide

---

## 🔧 CORRECTIONS REQUISES

### 1. Erreurs ObjectCreate (Lignes 386, 402, 423)

**❌ ERREUR COMMUNE :**
```cpp
// Utilisation de constantes inexistantes
ObjectCreate(0, "name", SOME_UNDEFINED_TYPE, 0, 0, 0);
```

**✅ CORRECTION :**
```cpp
// Types d'objets valides en MQL5
ObjectCreate(0, "name", OBJ_HLINE, 0, 0, 0);        // Ligne horizontale
ObjectCreate(0, "name", OBJ_VLINE, 0, TimeCurrent(), 0);  // Ligne verticale
ObjectCreate(0, "name", OBJ_TREND, 0, 0, 0, 0, 0);  // Ligne de tendance
ObjectCreate(0, "name", OBJ_RECTANGLE, 0, 0, 0, 0, 0);  // Rectangle
ObjectCreate(0, "name", OBJ_LABEL, 0, 0, 0);        // Label texte
ObjectCreate(0, "name", OBJ_TEXT, 0, 0, 0);         // Texte
```

### 2. Erreurs ObjectSetInteger (Lignes 396-397, 412-413, 433-434)

**❌ ERREUR COMMUNE :**
```cpp
// Utilisation de propriétés inexistantes
ObjectSetInteger(0, "name", SOME_UNDEFINED_PROP, value);
```

**✅ CORRECTION :**
```cpp
// Propriétés valides en MQL5
ObjectSetInteger(0, "name", OBJPROP_COLOR, clrRed);           // Couleur
ObjectSetInteger(0, "name", OBJPROP_STYLE, STYLE_SOLID);      // Style de ligne
ObjectSetInteger(0, "name", OBJPROP_WIDTH, 2);                // Largeur
ObjectSetInteger(0, "name", OBJPROP_BACK, false);             // Arrière-plan
ObjectSetInteger(0, "name", OBJPROP_SELECTABLE, true);        // Sélectionnable
ObjectSetInteger(0, "name", OBJPROP_SELECTED, false);         // Sélectionné
ObjectSetInteger(0, "name", OBJPROP_HIDDEN, false);           // Caché
ObjectSetInteger(0, "name", OBJPROP_ZORDER, 0);               // Ordre Z
ObjectSetInteger(0, "name", OBJPROP_FILL, true);              // Remplissage
ObjectSetInteger(0, "name", OBJPROP_CORNER, CORNER_LEFT_UPPER);  // Coin d'ancrage
ObjectSetInteger(0, "name", OBJPROP_ANCHOR, ANCHOR_LEFT_UPPER);  // Point d'ancrage
```

---

## 🎯 PATCH AUTOMATIQUE

Voici un script de recherche/remplacement pour corriger automatiquement les erreurs courantes :

### Ligne 386 (supposée)
```cpp
// SI VOUS AVEZ :
ObjectCreate(0, scope_name, OBJ_ELLIPSE_BY_ANGLE, ...);

// REMPLACER PAR (exemple pour un cercle) :
if(!ObjectCreate(0, scope_name, OBJ_ELLIPSE_BY_ANGLE, 0, 
                 TimeCurrent(), scope_price, TimeCurrent() + PeriodSeconds()*100, scope_price,
                 0, 360))  // Angles 0-360 pour cercle complet
{
   Print("Erreur création scope : ", GetLastError());
   return;
}
```

### Lignes 396-397 (supposées)
```cpp
// SI VOUS AVEZ :
ObjectSetInteger(0, scope_name, OBJPROP_ELLIPSE_SCALE, ...);

// REMPLACER PAR :
ObjectSetInteger(0, scope_name, OBJPROP_FILL, false);        // Pas de remplissage
ObjectSetInteger(0, scope_name, OBJPROP_COLOR, clrYellow);   // Couleur du contour
ObjectSetInteger(0, scope_name, OBJPROP_STYLE, STYLE_SOLID); // Style ligne solide
ObjectSetInteger(0, scope_name, OBJPROP_WIDTH, 2);           // Largeur 2 pixels
```

### Ligne 402 (supposée)
```cpp
// SI VOUS CRÉEZ UN LABEL :
if(!ObjectCreate(0, label_name, OBJ_LABEL, 0, 0, 0))
{
   Print("Erreur création label : ", GetLastError());
   return;
}

// Puis configurez-le :
ObjectSetInteger(0, label_name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
ObjectSetInteger(0, label_name, OBJPROP_XDISTANCE, 10);
ObjectSetInteger(0, label_name, OBJPROP_YDISTANCE, 10);
ObjectSetInteger(0, label_name, OBJPROP_COLOR, clrWhite);
ObjectSetString(0, label_name, OBJPROP_TEXT, "ALGIZ ACTIVÉ");
ObjectSetString(0, label_name, OBJPROP_FONT, "Arial Bold");
ObjectSetInteger(0, label_name, OBJPROP_FONTSIZE, 12);
```

### Lignes 412-413 (supposées)
```cpp
// Configuration d'une ligne horizontale
ObjectSetInteger(0, hline_name, OBJPROP_COLOR, clrRed);
ObjectSetInteger(0, hline_name, OBJPROP_STYLE, STYLE_DASH);
ObjectSetInteger(0, hline_name, OBJPROP_WIDTH, 1);
ObjectSetInteger(0, hline_name, OBJPROP_BACK, true);  // Arrière-plan
ObjectSetInteger(0, hline_name, OBJPROP_SELECTABLE, false);
ObjectSetInteger(0, hline_name, OBJPROP_RAY_RIGHT, true);  // Prolonger à droite
```

### Ligne 423 (supposée)
```cpp
// SI VOUS CRÉEZ UN RECTANGLE :
if(!ObjectCreate(0, rect_name, OBJ_RECTANGLE, 0,
                 time1, price1,  // Coin supérieur gauche
                 time2, price2)) // Coin inférieur droit
{
   Print("Erreur création rectangle : ", GetLastError());
   return;
}
```

### Lignes 433-434 (supposées)
```cpp
// Configuration d'un rectangle
ObjectSetInteger(0, rect_name, OBJPROP_COLOR, clrDodgerBlue);
ObjectSetInteger(0, rect_name, OBJPROP_STYLE, STYLE_SOLID);
ObjectSetInteger(0, rect_name, OBJPROP_WIDTH, 2);
ObjectSetInteger(0, rect_name, OBJPROP_FILL, true);        // Avec remplissage
ObjectSetInteger(0, rect_name, OBJPROP_BACK, false);       // Au premier plan
ObjectSetInteger(0, rect_name, OBJPROP_BGCOLOR, clrLightBlue);  // Couleur fond
```

---

## 📋 CHECKLIST DE VÉRIFICATION

### ✅ Types d'Objets Valides (ENUM_OBJECT)
- [ ] OBJ_VLINE - Ligne verticale
- [ ] OBJ_HLINE - Ligne horizontale  
- [ ] OBJ_TREND - Ligne de tendance
- [ ] OBJ_TRENDBYANGLE - Tendance par angle
- [ ] OBJ_RECTANGLE - Rectangle
- [ ] OBJ_TRIANGLE - Triangle
- [ ] OBJ_ELLIPSE - Ellipse
- [ ] OBJ_ELLIPSE_BY_ANGLE - Ellipse par angles (pour cercles)
- [ ] OBJ_CHANNEL - Canal équidistant
- [ ] OBJ_STDDEVCHANNEL - Canal de déviation standard
- [ ] OBJ_REGRESSION - Canal de régression
- [ ] OBJ_PITCHFORK - Fourche d'Andrews
- [ ] OBJ_GANNLINE - Ligne de Gann
- [ ] OBJ_GANNFAN - Éventail de Gann
- [ ] OBJ_GANNGRID - Grille de Gann
- [ ] OBJ_FIBO - Retracement de Fibonacci
- [ ] OBJ_FIBOTIMES - Zones temporelles de Fibonacci
- [ ] OBJ_FIBOFAN - Éventail de Fibonacci
- [ ] OBJ_FIBOARC - Arcs de Fibonacci
- [ ] OBJ_FIBOCHANNEL - Canal de Fibonacci
- [ ] OBJ_EXPANSION - Extension de Fibonacci
- [ ] OBJ_ARROW - Flèche
- [ ] OBJ_ARROW_THUMB_UP - Pouce levé
- [ ] OBJ_ARROW_THUMB_DOWN - Pouce baissé
- [ ] OBJ_ARROW_UP - Flèche haut
- [ ] OBJ_ARROW_DOWN - Flèche bas
- [ ] OBJ_ARROW_STOP - Stop
- [ ] OBJ_ARROW_CHECK - Coche
- [ ] OBJ_ARROW_LEFT_PRICE - Prix gauche
- [ ] OBJ_ARROW_RIGHT_PRICE - Prix droit
- [ ] OBJ_ARROW_BUY - Achat
- [ ] OBJ_ARROW_SELL - Vente
- [ ] OBJ_TEXT - Texte
- [ ] OBJ_LABEL - Label (étiquette)
- [ ] OBJ_BUTTON - Bouton
- [ ] OBJ_CHART - Sous-graphique
- [ ] OBJ_BITMAP - Image bitmap
- [ ] OBJ_BITMAP_LABEL - Label bitmap
- [ ] OBJ_EDIT - Zone d'édition
- [ ] OBJ_EVENT - Événement
- [ ] OBJ_RECTANGLE_LABEL - Label rectangulaire

### ✅ Propriétés d'Objets Valides (ENUM_OBJECT_PROPERTY_INTEGER)
- [ ] OBJPROP_COLOR - Couleur
- [ ] OBJPROP_STYLE - Style de ligne
- [ ] OBJPROP_WIDTH - Largeur de ligne
- [ ] OBJPROP_BACK - Arrière-plan
- [ ] OBJPROP_ZORDER - Ordre Z
- [ ] OBJPROP_FILL - Remplissage
- [ ] OBJPROP_HIDDEN - Caché dans la liste
- [ ] OBJPROP_SELECTED - Sélectionné
- [ ] OBJPROP_READONLY - Lecture seule
- [ ] OBJPROP_TYPE - Type d'objet
- [ ] OBJPROP_TIME - Temps (coordonnée temporelle)
- [ ] OBJPROP_SELECTABLE - Peut être sélectionné
- [ ] OBJPROP_CREATETIME - Heure de création
- [ ] OBJPROP_LEVELS - Nombre de niveaux
- [ ] OBJPROP_LEVELCOLOR - Couleur du niveau
- [ ] OBJPROP_LEVELSTYLE - Style du niveau
- [ ] OBJPROP_LEVELWIDTH - Largeur du niveau
- [ ] OBJPROP_ALIGN - Alignement du texte
- [ ] OBJPROP_FONTSIZE - Taille de police
- [ ] OBJPROP_RAY_LEFT - Prolonger à gauche
- [ ] OBJPROP_RAY_RIGHT - Prolonger à droite
- [ ] OBJPROP_RAY - Rayon (ligne infinie)
- [ ] OBJPROP_ELLIPSE - Ellipse
- [ ] OBJPROP_ARROWCODE - Code de flèche
- [ ] OBJPROP_TIMEFRAMES - Timeframes visibles
- [ ] OBJPROP_ANCHOR - Point d'ancrage
- [ ] OBJPROP_XDISTANCE - Distance X en pixels
- [ ] OBJPROP_YDISTANCE - Distance Y en pixels
- [ ] OBJPROP_DIRECTION - Direction
- [ ] OBJPROP_DEGREE - Degrés
- [ ] OBJPROP_DRAWLINES - Dessiner les lignes
- [ ] OBJPROP_STATE - État (bouton pressé)
- [ ] OBJPROP_CHART_ID - ID du graphique
- [ ] OBJPROP_XSIZE - Taille X
- [ ] OBJPROP_YSIZE - Taille Y
- [ ] OBJPROP_XOFFSET - Décalage X
- [ ] OBJPROP_YOFFSET - Décalage Y
- [ ] OBJPROP_PERIOD - Période
- [ ] OBJPROP_DATE_SCALE - Échelle de date
- [ ] OBJPROP_PRICE_SCALE - Échelle de prix
- [ ] OBJPROP_CHART_SCALE - Échelle du graphique
- [ ] OBJPROP_BGCOLOR - Couleur d'arrière-plan
- [ ] OBJPROP_CORNER - Coin d'ancrage
- [ ] OBJPROP_BORDER_TYPE - Type de bordure
- [ ] OBJPROP_BORDER_COLOR - Couleur de bordure

---

## 🔨 MÉTHODE DE CORRECTION MANUELLE

### Étape 1 : Ouvrir ALGIZ.mq5 dans MetaEditor

### Étape 2 : Pour chaque ligne d'erreur, identifier le type de correction :

**Pour les ObjectCreate :**
1. Vérifier le type d'objet utilisé
2. Remplacer par un type valide de la liste ci-dessus
3. Adapter les paramètres selon le type

**Pour les ObjectSetInteger :**
1. Vérifier la propriété utilisée
2. Remplacer par une propriété valide de la liste ci-dessus
3. Vérifier que la valeur est compatible

### Étape 3 : Compiler et tester

```cpp
// Exemple de fonction de test
void TestObjectCreation()
{
   // Test création cercle
   string circle_name = "TEST_CIRCLE";
   double test_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   datetime test_time = TimeCurrent();
   
   if(ObjectCreate(0, circle_name, OBJ_ELLIPSE_BY_ANGLE, 0,
                   test_time, test_price,
                   test_time + PeriodSeconds()*50, test_price,
                   0, 360))
   {
      ObjectSetInteger(0, circle_name, OBJPROP_COLOR, clrYellow);
      ObjectSetInteger(0, circle_name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, circle_name, OBJPROP_WIDTH, 2);
      ObjectSetInteger(0, circle_name, OBJPROP_FILL, false);
      Print("✅ Cercle créé avec succès");
   }
   else
   {
      Print("❌ Erreur création cercle : ", GetLastError());
   }
}
```

---

## 🚀 TEMPLATE DE REMPLACEMENT RAPIDE

### Pattern de Recherche/Remplacement dans MetaEditor

**Recherche 1 :** Lignes avec ObjectCreate utilisant des constantes invalides
**Remplacement :** Utiliser OBJ_ELLIPSE_BY_ANGLE pour les cercles, OBJ_LABEL pour les textes

**Recherche 2 :** Lignes avec ObjectSetInteger utilisant des propriétés invalides
**Remplacement :** Utiliser OBJPROP_COLOR, OBJPROP_STYLE, OBJPROP_WIDTH selon le contexte

---

## 📞 AIDE SUPPLÉMENTAIRE

Si vous avez besoin d'une correction spécifique, fournissez-moi :
1. Le code source d'ALGIZ.mq5 (ou les lignes 380-440)
2. Ce que vous essayez de dessiner (cercle, ligne, label, etc.)
3. L'effet visuel souhaité

Je pourrai alors générer le code exact à utiliser.

---

## ✅ VÉRIFICATION FINALE

Une fois les corrections appliquées :
1. **Compiler** (F7 dans MetaEditor)
2. **Vérifier** : 0 erreurs, 0 warnings
3. **Tester** sur un graphique demo
4. **Valider** que les objets s'affichent correctement

**Code Algiz Ehlaz - Protection Activée** 🛡️
