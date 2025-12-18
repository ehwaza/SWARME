//+------------------------------------------------------------------+
//|                                          SNIPER_SCOPE_SWARNE.mq5 |
//|                                    Viseur Laser pour SWARNE V2   |
//|                                     Copyright © 2024, Sniper Team|
//+------------------------------------------------------------------+
#property copyright "Copyright © 2024, Sniper Team - SWARNE Edition"
#property version   "2.00"
#property description "Sniper Scope pour SWARNE - Signaux de Précision"
#property indicator_chart_window
#property indicator_plots 0

//+------------------------------------------------------------------+
//| INPUT PARAMETERS                                                 |
//+------------------------------------------------------------------+
input color LASER_COLOR = clrRed;           // Couleur du laser
input int   SIGNAL_PERIOD = 5;              // Période des signaux
input bool  AUTO_TRACKING = true;           // Suivi automatique
input double PROFIT_TARGET_PIPS = 1.0;      // Target en pips pour sortie
input double STOP_LOSS_PIPS = 1.5;          // Stop loss en pips

//+------------------------------------------------------------------+
//| GLOBAL VARIABLES                                                 |
//+------------------------------------------------------------------+
double laserPrice = 0.0;
datetime laserTime = 0;
string signalDirection = "HOLD";
double signalStrength = 0.0;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
{
   // Initialiser le laser
   laserPrice = SymbolInfoDouble(Symbol(), SYMBOL_BID);
   laserTime = TimeCurrent();
   
   // Créer le laser horizontal
   ObjectCreate(0, "SWARNE_Laser_H", OBJ_HLINE, 0, 0, laserPrice);
   ObjectSetInteger(0, "SWARNE_Laser_H", OBJPROP_COLOR, LASER_COLOR);
   ObjectSetInteger(0, "SWARNE_Laser_H", OBJPROP_STYLE, STYLE_SOLID);
   ObjectSetInteger(0, "SWARNE_Laser_H", OBJPROP_WIDTH, 2);
   
   // Créer le laser vertical
   ObjectCreate(0, "SWARNE_Laser_V", OBJ_VLINE, 0, laserTime, 0);
   ObjectSetInteger(0, "SWARNE_Laser_V", OBJPROP_COLOR, LASER_COLOR);
   ObjectSetInteger(0, "SWARNE_Laser_V", OBJPROP_STYLE, STYLE_SOLID);
   ObjectSetInteger(0, "SWARNE_Laser_V", OBJPROP_WIDTH, 2);
   
   // Créer affichage signal
   ObjectCreate(0, "SWARNE_Signal", OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, "SWARNE_Signal", OBJPROP_CORNER, CORNER_RIGHT_UPPER);
   ObjectSetInteger(0, "SWARNE_Signal", OBJPROP_XDISTANCE, 20);
   ObjectSetInteger(0, "SWARNE_Signal", OBJPROP_YDISTANCE, 20);
   ObjectSetString(0, "SWARNE_Signal", OBJPROP_TEXT, "SIGNAL: HOLD");
   ObjectSetString(0, "SWARNE_Signal", OBJPROP_FONT, "Arial Black");
   ObjectSetInteger(0, "SWARNE_Signal", OBJPROP_FONTSIZE, 12);
   ObjectSetInteger(0, "SWARNE_Signal", OBJPROP_COLOR, clrYellow);
   
   // Créer affichage force
   ObjectCreate(0, "SWARNE_Strength", OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, "SWARNE_Strength", OBJPROP_CORNER, CORNER_RIGHT_UPPER);
   ObjectSetInteger(0, "SWARNE_Strength", OBJPROP_XDISTANCE, 20);
   ObjectSetInteger(0, "SWARNE_Strength", OBJPROP_YDISTANCE, 40);
   ObjectSetString(0, "SWARNE_Strength", OBJPROP_TEXT, "FORCE: 0%");
   ObjectSetString(0, "SWARNE_Strength", OBJPROP_FONT, "Arial");
   ObjectSetInteger(0, "SWARNE_Strength", OBJPROP_FONTSIZE, 10);
   ObjectSetInteger(0, "SWARNE_Strength", OBJPROP_COLOR, clrWhite);
   
   Print("🎯 SNIPER SCOPE SWARNE v2.0 - ACTIF");
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   ObjectDelete(0, "SWARNE_Laser_H");
   ObjectDelete(0, "SWARNE_Laser_V");
   ObjectDelete(0, "SWARNE_Signal");
   ObjectDelete(0, "SWARNE_Strength");
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
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
   // Mettre à jour le laser si auto-tracking
   if(AUTO_TRACKING)
   {
      double currentPrice = SymbolInfoDouble(Symbol(), SYMBOL_BID);
      laserPrice = currentPrice;
      laserTime = TimeCurrent();
      
      ObjectSetDouble(0, "SWARNE_Laser_H", OBJPROP_PRICE, laserPrice);
      ObjectSetInteger(0, "SWARNE_Laser_V", OBJPROP_TIME, laserTime);
   }
   
   // Calculer le signal
   CalculateSignal(close, rates_total);
   
   // Mettre à jour l'affichage
   UpdateDisplay();
   
   // Écrire dans fichier pour SWARNE Python
   WriteSignalToFile();
   
   return rates_total;
}

//+------------------------------------------------------------------+
//| Calculer le signal de trading                                    |
//+------------------------------------------------------------------+
void CalculateSignal(const double &close[], int total)
{
   if(total < SIGNAL_PERIOD + 10)
   {
      signalDirection = "HOLD";
      signalStrength = 0.0;
      return;
   }
   
   // Calculer SMA rapide
   double smaFast = 0;
   for(int i = 1; i <= SIGNAL_PERIOD; i++)
   {
      smaFast += close[total - i];
   }
   smaFast /= SIGNAL_PERIOD;
   
   // Calculer SMA lente
   double smaSlow = 0;
   for(int i = 1; i <= SIGNAL_PERIOD * 2; i++)
   {
      smaSlow += close[total - i];
   }
   smaSlow /= (SIGNAL_PERIOD * 2);
   
   // Prix actuel
   double currentPrice = close[total - 1];
   
   // Déterminer signal
   if(currentPrice > smaFast && smaFast > smaSlow)
   {
      signalDirection = "BUY";
      signalStrength = MathMin((currentPrice - smaSlow) / smaSlow * 10000, 100);
   }
   else if(currentPrice < smaFast && smaFast < smaSlow)
   {
      signalDirection = "SELL";
      signalStrength = MathMin((smaSlow - currentPrice) / smaSlow * 10000, 100);
   }
   else
   {
      signalDirection = "HOLD";
      signalStrength = 0;
   }
}

//+------------------------------------------------------------------+
//| Mettre à jour l'affichage                                        |
//+------------------------------------------------------------------+
void UpdateDisplay()
{
   // Couleur selon signal
   color signalColor = clrYellow;
   if(signalDirection == "BUY") signalColor = clrLime;
   else if(signalDirection == "SELL") signalColor = clrRed;
   
   // Texte signal
   string signalText = "SIGNAL: " + signalDirection;
   if(signalStrength >= 80) signalText += " 🔥";
   ObjectSetString(0, "SWARNE_Signal", OBJPROP_TEXT, signalText);
   ObjectSetInteger(0, "SWARNE_Signal", OBJPROP_COLOR, signalColor);
   
   // Texte force
   string strengthText = StringFormat("FORCE: %.0f%%", signalStrength);
   ObjectSetString(0, "SWARNE_Strength", OBJPROP_TEXT, strengthText);
}

//+------------------------------------------------------------------+
//| Écrire le signal dans un fichier pour Python                     |
//+------------------------------------------------------------------+
void WriteSignalToFile()
{
   // Créer JSON pour SWARNE Python
   string jsonSignal = StringFormat(
      "{\"signal\":\"%s\",\"strength\":%.2f,\"price\":%.5f,\"time\":\"%s\",\"profit_target\":%.5f,\"stop_loss\":%.5f}",
      signalDirection,
      signalStrength,
      laserPrice,
      TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS),
      laserPrice + (signalDirection == "BUY" ? 1 : -1) * PROFIT_TARGET_PIPS * Point() * 10,
      laserPrice + (signalDirection == "BUY" ? -1 : 1) * STOP_LOSS_PIPS * Point() * 10
   );
   
   // Écrire dans fichier
   int fileHandle = FileOpen("SWARNE_SNIPER_SIGNAL.json", FILE_WRITE|FILE_TXT|FILE_COMMON);
   if(fileHandle != INVALID_HANDLE)
   {
      FileWriteString(fileHandle, jsonSignal);
      FileClose(fileHandle);
   }
}
//+------------------------------------------------------------------+
