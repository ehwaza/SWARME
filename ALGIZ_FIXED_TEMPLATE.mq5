//+------------------------------------------------------------------+
//|                                           ALGIZ_FIXED_TEMPLATE.mq5 |
//|                                    Template Corrigé pour ALGIZ     |
//|                                         Code Algiz Ehlaz 🛡️        |
//+------------------------------------------------------------------+
#property copyright "SWARNE! Community"
#property link      "https://github.com/swarne"
#property version   "1.01"
#property indicator_chart_window
#property indicator_plots 0

//+------------------------------------------------------------------+
//| EXEMPLE DE CORRECTIONS POUR LES ERREURS COMMUNES                  |
//+------------------------------------------------------------------+

// ============================================================
// VARIABLES GLOBALES
// ============================================================
string scope_name = "ALGIZ_SCOPE";
string label_name = "ALGIZ_LABEL";
string hline_name = "ALGIZ_HLINE";
string vline_name = "ALGIZ_VLINE";
string rect_name = "ALGIZ_RECT";

color scope_color = clrYellow;
color label_color = clrWhite;
color line_color = clrRed;

int scope_width = 2;
int line_width = 1;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                          |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("🛡️ ALGIZ Initialisé - Code Algiz Ehlaz Activé");
   
   // Créer les objets graphiques
   CreateScopeCircle();
   CreateInfoLabel();
   CreateProtectionLines();
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                        |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // Nettoyer tous les objets ALGIZ
   DeleteAllAlgizObjects();
   Print("🛡️ ALGIZ Désactivé");
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                               |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
   // Mise à jour des objets si nécessaire
   UpdateScopePosition();
   
   return(rates_total);
}

//+------------------------------------------------------------------+
//| CORRECTION 1 : Création d'un Cercle (SCOPE)                      |
//| ❌ AVANT : ObjectCreate avec type invalide                        |
//| ✅ APRÈS : OBJ_ELLIPSE_BY_ANGLE correctement configuré            |
//+------------------------------------------------------------------+
void CreateScopeCircle()
{
   double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   datetime current_time = TimeCurrent();
   int period_seconds = PeriodSeconds();
   
   // CORRECTION LIGNE 386 : Création du cercle
   if(!ObjectCreate(0, scope_name, OBJ_ELLIPSE_BY_ANGLE, 0,
                    current_time, current_price,                    // Centre
                    current_time + period_seconds * 100, current_price,  // Rayon
                    0, 360))  // Angles : 0-360° pour cercle complet
   {
      Print("❌ Erreur création scope : ", GetLastError());
      return;
   }
   
   // CORRECTION LIGNES 396-397 : Configuration du cercle
   ObjectSetInteger(0, scope_name, OBJPROP_COLOR, scope_color);
   ObjectSetInteger(0, scope_name, OBJPROP_STYLE, STYLE_SOLID);
   ObjectSetInteger(0, scope_name, OBJPROP_WIDTH, scope_width);
   ObjectSetInteger(0, scope_name, OBJPROP_FILL, false);  // Pas de remplissage
   ObjectSetInteger(0, scope_name, OBJPROP_BACK, false);  // Au premier plan
   ObjectSetInteger(0, scope_name, OBJPROP_SELECTABLE, true);
   ObjectSetInteger(0, scope_name, OBJPROP_SELECTED, false);
   ObjectSetInteger(0, scope_name, OBJPROP_HIDDEN, false);
   ObjectSetInteger(0, scope_name, OBJPROP_ZORDER, 0);
   
   Print("✅ Scope créé avec succès");
}

//+------------------------------------------------------------------+
//| CORRECTION 2 : Création d'un Label (Texte)                       |
//| ❌ AVANT : ObjectCreate avec type invalide                        |
//| ✅ APRÈS : OBJ_LABEL correctement configuré                       |
//+------------------------------------------------------------------+
void CreateInfoLabel()
{
   // CORRECTION LIGNE 402 : Création du label
   if(!ObjectCreate(0, label_name, OBJ_LABEL, 0, 0, 0))
   {
      Print("❌ Erreur création label : ", GetLastError());
      return;
   }
   
   // CORRECTION LIGNES 412-413 : Configuration du label
   ObjectSetInteger(0, label_name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, label_name, OBJPROP_XDISTANCE, 20);
   ObjectSetInteger(0, label_name, OBJPROP_YDISTANCE, 20);
   ObjectSetInteger(0, label_name, OBJPROP_COLOR, label_color);
   ObjectSetInteger(0, label_name, OBJPROP_FONTSIZE, 12);
   ObjectSetInteger(0, label_name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, label_name, OBJPROP_BACK, false);
   ObjectSetInteger(0, label_name, OBJPROP_HIDDEN, false);
   
   ObjectSetString(0, label_name, OBJPROP_TEXT, "🛡️ ALGIZ ACTIVÉ");
   ObjectSetString(0, label_name, OBJPROP_FONT, "Arial Bold");
   
   Print("✅ Label créé avec succès");
}

//+------------------------------------------------------------------+
//| CORRECTION 3 : Création de Lignes de Protection                  |
//| ❌ AVANT : ObjectCreate avec types invalides                      |
//| ✅ APRÈS : OBJ_HLINE et OBJ_VLINE correctement configurés        |
//+------------------------------------------------------------------+
void CreateProtectionLines()
{
   double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   datetime current_time = TimeCurrent();
   
   // CORRECTION LIGNE 423 : Ligne horizontale (Support/Résistance)
   if(!ObjectCreate(0, hline_name, OBJ_HLINE, 0, 0, current_price))
   {
      Print("❌ Erreur création hline : ", GetLastError());
      return;
   }
   
   // CORRECTION LIGNES 433-434 : Configuration de la ligne horizontale
   ObjectSetInteger(0, hline_name, OBJPROP_COLOR, line_color);
   ObjectSetInteger(0, hline_name, OBJPROP_STYLE, STYLE_DASH);
   ObjectSetInteger(0, hline_name, OBJPROP_WIDTH, line_width);
   ObjectSetInteger(0, hline_name, OBJPROP_BACK, true);  // En arrière-plan
   ObjectSetInteger(0, hline_name, OBJPROP_SELECTABLE, true);
   ObjectSetInteger(0, hline_name, OBJPROP_RAY_RIGHT, true);  // Prolonger à droite
   
   ObjectSetString(0, hline_name, OBJPROP_TEXT, "Protection Level");
   
   // Ligne verticale (Événement temporel)
   if(!ObjectCreate(0, vline_name, OBJ_VLINE, 0, current_time, 0))
   {
      Print("❌ Erreur création vline : ", GetLastError());
      return;
   }
   
   ObjectSetInteger(0, vline_name, OBJPROP_COLOR, clrBlue);
   ObjectSetInteger(0, vline_name, OBJPROP_STYLE, STYLE_DOT);
   ObjectSetInteger(0, vline_name, OBJPROP_WIDTH, 1);
   ObjectSetInteger(0, vline_name, OBJPROP_BACK, true);
   ObjectSetInteger(0, vline_name, OBJPROP_SELECTABLE, false);
   
   Print("✅ Lignes de protection créées avec succès");
}

//+------------------------------------------------------------------+
//| Mise à jour de la position du scope                              |
//+------------------------------------------------------------------+
void UpdateScopePosition()
{
   // Vérifier si le scope existe
   if(ObjectFind(0, scope_name) < 0)
      return;
   
   double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   datetime current_time = TimeCurrent();
   int period_seconds = PeriodSeconds();
   
   // Mettre à jour la position du centre
   ObjectSetDouble(0, scope_name, OBJPROP_PRICE, 0, current_price);
   ObjectSetInteger(0, scope_name, OBJPROP_TIME, 0, current_time);
   
   // Mettre à jour le rayon
   ObjectSetDouble(0, scope_name, OBJPROP_PRICE, 1, current_price);
   ObjectSetInteger(0, scope_name, OBJPROP_TIME, 1, current_time + period_seconds * 100);
   
   // Redessiner le graphique
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| Supprimer tous les objets ALGIZ                                  |
//+------------------------------------------------------------------+
void DeleteAllAlgizObjects()
{
   ObjectDelete(0, scope_name);
   ObjectDelete(0, label_name);
   ObjectDelete(0, hline_name);
   ObjectDelete(0, vline_name);
   ObjectDelete(0, rect_name);
   
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| EXEMPLE BONUS : Rectangle de Zone                                |
//+------------------------------------------------------------------+
void CreateProtectionZone(datetime time1, double price1, 
                          datetime time2, double price2)
{
   // Créer un rectangle pour une zone de protection
   if(!ObjectCreate(0, rect_name, OBJ_RECTANGLE, 0,
                    time1, price1,  // Coin supérieur gauche
                    time2, price2)) // Coin inférieur droit
   {
      Print("❌ Erreur création rectangle : ", GetLastError());
      return;
   }
   
   // Configuration du rectangle
   ObjectSetInteger(0, rect_name, OBJPROP_COLOR, clrDodgerBlue);
   ObjectSetInteger(0, rect_name, OBJPROP_STYLE, STYLE_SOLID);
   ObjectSetInteger(0, rect_name, OBJPROP_WIDTH, 2);
   ObjectSetInteger(0, rect_name, OBJPROP_FILL, true);  // Avec remplissage
   ObjectSetInteger(0, rect_name, OBJPROP_BACK, false); // Au premier plan
   ObjectSetInteger(0, rect_name, OBJPROP_BGCOLOR, clrLightBlue);  // Couleur de fond
   ObjectSetInteger(0, rect_name, OBJPROP_SELECTABLE, true);
   ObjectSetInteger(0, rect_name, OBJPROP_HIDDEN, false);
   
   Print("✅ Zone de protection créée avec succès");
}

//+------------------------------------------------------------------+
//| GESTION DES ÉVÉNEMENTS CLAVIER                                    |
//+------------------------------------------------------------------+
void OnChartEvent(const int id,
                  const long &lparam,
                  const double &dparam,
                  const string &sparam)
{
   // Exemple : ESPACE pour toggle le scope
   if(id == CHARTEVENT_KEYDOWN)
   {
      if(lparam == 32)  // Touche ESPACE
      {
         bool is_visible = ObjectGetInteger(0, scope_name, OBJPROP_TIMEFRAMES) != OBJ_NO_PERIODS;
         
         if(is_visible)
         {
            ObjectSetInteger(0, scope_name, OBJPROP_TIMEFRAMES, OBJ_NO_PERIODS);
            Print("🛡️ Scope masqué");
         }
         else
         {
            ObjectSetInteger(0, scope_name, OBJPROP_TIMEFRAMES, OBJ_ALL_PERIODS);
            Print("🛡️ Scope visible");
         }
         
         ChartRedraw(0);
      }
   }
}

//+------------------------------------------------------------------+
//|                      FIN DU TEMPLATE CORRIGÉ                      |
//|                     🛡️ Code Algiz Ehlaz 🛡️                        |
//+------------------------------------------------------------------+
