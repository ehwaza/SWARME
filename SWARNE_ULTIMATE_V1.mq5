//+------------------------------------------------------------------+
//|                                        SWARNE_ULTIMATE_V1.mq5    |
//|                    SNIPER SCOPE + GOLDENEYE - VERSION UNIFIÉE    |
//|                                    Mathieu - Swarne! Project     |
//+------------------------------------------------------------------+
#property copyright "Mathieu - Swarne! Ultimate"
#property link      "https://github.com/swarne"
#property version   "1.00"
#property indicator_chart_window
#property indicator_buffers 10
#property indicator_plots   6

// Plots
#property indicator_label1  "EMA Fast"
#property indicator_type1   DRAW_LINE
#property indicator_color1  clrDodgerBlue
#property indicator_style1  STYLE_SOLID
#property indicator_width1  2

#property indicator_label2  "EMA Slow"
#property indicator_type2   DRAW_LINE
#property indicator_color2  clrRed
#property indicator_style2  STYLE_SOLID
#property indicator_width2  2

#property indicator_label3  "BUY Signal"
#property indicator_type3   DRAW_ARROW
#property indicator_color3  clrLime
#property indicator_width3  4

#property indicator_label4  "SELL Signal"
#property indicator_type4   DRAW_ARROW
#property indicator_color4  clrRed
#property indicator_width4  4

#property indicator_label5  "Stop Loss"
#property indicator_type5   DRAW_LINE
#property indicator_color5  clrDarkRed
#property indicator_style5  STYLE_DOT
#property indicator_width5  1

#property indicator_label6  "Take Profit"
#property indicator_type6   DRAW_LINE
#property indicator_color6  clrDarkGreen
#property indicator_style6  STYLE_DOT
#property indicator_width6  1

//--- Inputs
input group "🎯 GOLDENEYE Settings"
input int      InpEMA_Fast          = 9;        // EMA Fast Period
input int      InpEMA_Slow          = 21;       // EMA Slow Period
input int      InpADX_Period        = 14;       // ADX Period
input double   InpADX_Threshold     = 25.0;     // ADX Threshold

input group "🔫 SNIPER SCOPE Settings"
input int      ScopeRadius          = 150;      // Scope Radius (pixels)
input color    ScopeColor           = clrWhite; // Scope Color
input int      ScopeThickness       = 2;        // Scope Line Thickness
input bool     ShowKillZone         = true;     // Show Kill Zone
input double   TensionThreshold     = 0.65;     // Tension Threshold for FIRE

input group "🛡️ RISK MANAGER Settings"
input double   RiskPerTrade         = 1.0;      // Risk per Trade (%)
input double   StopLossATR          = 1.5;      // Stop Loss (ATR multiplier)
input double   TakeProfitATR        = 2.5;      // Take Profit (ATR multiplier)

input group "🎮 VISUAL Settings"
input bool     ShowPanel            = true;     // Show Info Panel
input int      PanelX               = 20;       // Panel X Position
input int      PanelY               = 50;       // Panel Y Position
input int      FontSize             = 10;       // Font Size
input bool     ShowAlerts           = true;     // Show Alerts

//--- Buffers
double EMA_Fast_Buffer[];
double EMA_Slow_Buffer[];
double BUY_Signal_Buffer[];
double SELL_Signal_Buffer[];
double StopLoss_Buffer[];
double TakeProfit_Buffer[];
double Tension_Buffer[];
double Confidence_Buffer[];
double RiskScore_Buffer[];
double ADX_Buffer[];

//--- Handles
int EMA_Fast_Handle = INVALID_HANDLE;
int EMA_Slow_Handle = INVALID_HANDLE;
int ADX_Handle = INVALID_HANDLE;
int ATR_Handle = INVALID_HANDLE;
int RSI_Handle = INVALID_HANDLE;

//--- Scope Variables
int ScopeCenterX = 400;
int ScopeCenterY = 300;
bool ScopeVisible = true;
double CurrentTension = 0.0;
double CurrentConfidence = 0.0;
string CurrentSignal = "WAIT";
bool BlinkState = false;
datetime LastAlertTime = 0;
int KillZoneRadius = 0;

//--- Object Prefix
string ObjPrefix = "SWARNE_";

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("=== SWARNE! ULTIMATE V1 - INITIALIZATION ===");
   
   //--- Set index buffers
   SetIndexBuffer(0, EMA_Fast_Buffer, INDICATOR_DATA);
   SetIndexBuffer(1, EMA_Slow_Buffer, INDICATOR_DATA);
   SetIndexBuffer(2, BUY_Signal_Buffer, INDICATOR_DATA);
   SetIndexBuffer(3, SELL_Signal_Buffer, INDICATOR_DATA);
   SetIndexBuffer(4, StopLoss_Buffer, INDICATOR_DATA);
   SetIndexBuffer(5, TakeProfit_Buffer, INDICATOR_DATA);
   SetIndexBuffer(6, Tension_Buffer, INDICATOR_CALCULATIONS);
   SetIndexBuffer(7, Confidence_Buffer, INDICATOR_CALCULATIONS);
   SetIndexBuffer(8, RiskScore_Buffer, INDICATOR_CALCULATIONS);
   SetIndexBuffer(9, ADX_Buffer, INDICATOR_CALCULATIONS);
   
   //--- Set arrow codes
   PlotIndexSetInteger(2, PLOT_ARROW, 233);  // Up arrow
   PlotIndexSetInteger(3, PLOT_ARROW, 234);  // Down arrow
   
   //--- Set empty values
   PlotIndexSetDouble(2, PLOT_EMPTY_VALUE, 0);
   PlotIndexSetDouble(3, PLOT_EMPTY_VALUE, 0);
   PlotIndexSetDouble(4, PLOT_EMPTY_VALUE, 0);
   PlotIndexSetDouble(5, PLOT_EMPTY_VALUE, 0);
   
   //--- Create indicator handles
   EMA_Fast_Handle = iMA(_Symbol, PERIOD_CURRENT, InpEMA_Fast, 0, MODE_EMA, PRICE_CLOSE);
   EMA_Slow_Handle = iMA(_Symbol, PERIOD_CURRENT, InpEMA_Slow, 0, MODE_EMA, PRICE_CLOSE);
   ADX_Handle = iADX(_Symbol, PERIOD_CURRENT, InpADX_Period);
   ATR_Handle = iATR(_Symbol, PERIOD_CURRENT, 14);
   RSI_Handle = iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
   
   if(EMA_Fast_Handle == INVALID_HANDLE || EMA_Slow_Handle == INVALID_HANDLE || 
      ADX_Handle == INVALID_HANDLE || ATR_Handle == INVALID_HANDLE)
   {
      Print("❌ Error creating indicator handles");
      return(INIT_FAILED);
   }
   
   //--- Initialize scope position (center of chart)
   long chart_id = ChartID();
   int width = (int)ChartGetInteger(chart_id, CHART_WIDTH_IN_PIXELS);
   int height = (int)ChartGetInteger(chart_id, CHART_HEIGHT_IN_PIXELS);
   
   if(width > 0 && height > 0)
   {
      ScopeCenterX = width / 2;
      ScopeCenterY = height / 2;
   }
   
   //--- Create visual panel
   if(ShowPanel)
      CreateInfoPanel();
   
   //--- Start timer
   EventSetTimer(1);
   
   Print("✅ SWARNE! ULTIMATE V1 initialized successfully");
   Print("📍 Scope position: X=", ScopeCenterX, " Y=", ScopeCenterY);
   
   return(INIT_SUCCEEDED);
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
   if(rates_total < 50) return(0);
   
   //--- Set arrays as series
   ArraySetAsSeries(EMA_Fast_Buffer, true);
   ArraySetAsSeries(EMA_Slow_Buffer, true);
   ArraySetAsSeries(BUY_Signal_Buffer, true);
   ArraySetAsSeries(SELL_Signal_Buffer, true);
   ArraySetAsSeries(StopLoss_Buffer, true);
   ArraySetAsSeries(TakeProfit_Buffer, true);
   ArraySetAsSeries(close, true);
   ArraySetAsSeries(high, true);
   ArraySetAsSeries(low, true);
   ArraySetAsSeries(time, true);
   
   //--- Copy indicator data
   if(CopyBuffer(EMA_Fast_Handle, 0, 0, rates_total, EMA_Fast_Buffer) <= 0 ||
      CopyBuffer(EMA_Slow_Handle, 0, 0, rates_total, EMA_Slow_Buffer) <= 0 ||
      CopyBuffer(ADX_Handle, 0, 0, rates_total, ADX_Buffer) <= 0)
   {
      return(0);
   }
   
   //--- Calculate tension and confidence
   CurrentTension = CalculateTension();
   CurrentConfidence = CalculateConfidence();
   
   //--- Process signals
   int start = (prev_calculated == 0) ? 1 : prev_calculated - 1;
   
   for(int i = start; i < rates_total && i >= 0; i++)
   {
      //--- Reset signal buffers
      BUY_Signal_Buffer[i] = 0;
      SELL_Signal_Buffer[i] = 0;
      StopLoss_Buffer[i] = 0;
      TakeProfit_Buffer[i] = 0;
      
      if(i >= rates_total - 1) continue;
      
      //--- Check for EMA crossover
      bool bullish_cross = (EMA_Fast_Buffer[i+1] <= EMA_Slow_Buffer[i+1]) && 
                          (EMA_Fast_Buffer[i] > EMA_Slow_Buffer[i]);
      bool bearish_cross = (EMA_Fast_Buffer[i+1] >= EMA_Slow_Buffer[i+1]) && 
                          (EMA_Fast_Buffer[i] < EMA_Slow_Buffer[i]);
      
      //--- Check ADX strength
      bool strong_trend = (ADX_Buffer[i] > InpADX_Threshold);
      
      //--- Calculate ATR for stops
      double atr[];
      ArraySetAsSeries(atr, true);
      CopyBuffer(ATR_Handle, 0, i, 1, atr);
      
      //--- BUY Signal
      if(bullish_cross && strong_trend && CurrentTension > TensionThreshold)
      {
         BUY_Signal_Buffer[i] = low[i] - (high[i] - low[i]) * 0.3;
         StopLoss_Buffer[i] = close[i] - atr[0] * StopLossATR;
         TakeProfit_Buffer[i] = close[i] + atr[0] * TakeProfitATR;
         
         //--- Alert on most recent bar
         if(i == 0 && ShowAlerts && time[0] != LastAlertTime)
         {
            Alert("🐝 SWARNE! BUY SIGNAL 🐝\n",
                  "Symbol: ", _Symbol, "\n",
                  "Price: ", DoubleToString(close[0], _Digits), "\n",
                  "Tension: ", IntegerToString((int)(CurrentTension * 100)), "%\n",
                  "Confidence: ", IntegerToString((int)(CurrentConfidence * 100)), "%");
            LastAlertTime = time[0];
            CurrentSignal = "BUY";
         }
      }
      
      //--- SELL Signal
      if(bearish_cross && strong_trend && CurrentTension > TensionThreshold)
      {
         SELL_Signal_Buffer[i] = high[i] + (high[i] - low[i]) * 0.3;
         StopLoss_Buffer[i] = close[i] + atr[0] * StopLossATR;
         TakeProfit_Buffer[i] = close[i] - atr[0] * TakeProfitATR;
         
         if(i == 0 && ShowAlerts && time[0] != LastAlertTime)
         {
            Alert("🐝 SWARNE! SELL SIGNAL 🐝\n",
                  "Symbol: ", _Symbol, "\n",
                  "Price: ", DoubleToString(close[0], _Digits), "\n",
                  "Tension: ", IntegerToString((int)(CurrentTension * 100)), "%\n",
                  "Confidence: ", IntegerToString((int)(CurrentConfidence * 100)), "%");
            LastAlertTime = time[0];
            CurrentSignal = "SELL";
         }
      }
   }
   
   //--- Update visual panel
   if(ShowPanel && rates_total > 0)
   {
      UpdateInfoPanel(close[0]);
   }
   
   return(rates_total);
}

//+------------------------------------------------------------------+
//| Calculate Tension (convergence indicator)                        |
//+------------------------------------------------------------------+
double CalculateTension()
{
   if(ArraySize(EMA_Fast_Buffer) < 2 || ArraySize(EMA_Slow_Buffer) < 2)
      return 0.0;
   
   double tension = 0.0;
   double price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   
   //--- 1. EMA Convergence (40%)
   double ema_distance = MathAbs(EMA_Fast_Buffer[0] - EMA_Slow_Buffer[0]);
   double normalized_distance = 1.0 - MathMin(ema_distance / (price * 0.01), 1.0);
   tension += normalized_distance * 0.4;
   
   //--- 2. Recent Crossover (30%)
   if(ArraySize(EMA_Fast_Buffer) > 1)
   {
      bool bullish_cross = (EMA_Fast_Buffer[1] <= EMA_Slow_Buffer[1]) && 
                          (EMA_Fast_Buffer[0] > EMA_Slow_Buffer[0]);
      bool bearish_cross = (EMA_Fast_Buffer[1] >= EMA_Slow_Buffer[1]) && 
                          (EMA_Fast_Buffer[0] < EMA_Slow_Buffer[0]);
      
      if(bullish_cross || bearish_cross)
         tension += 0.3;
   }
   
   //--- 3. RSI Neutrality (30%)
   double rsi[];
   ArraySetAsSeries(rsi, true);
   if(CopyBuffer(RSI_Handle, 0, 0, 1, rsi) > 0)
   {
      double rsi_neutral = 1.0 - MathAbs(rsi[0] - 50.0) / 50.0;
      tension += rsi_neutral * 0.3;
   }
   
   return MathMin(MathMax(tension, 0.0), 1.0);
}

//+------------------------------------------------------------------+
//| Calculate Confidence (signal strength)                           |
//+------------------------------------------------------------------+
double CalculateConfidence()
{
   if(ArraySize(ADX_Buffer) < 1) return 0.0;
   
   double confidence = 0.0;
   
   //--- 1. ADX Strength (40%)
   double adx_strength = MathMin(ADX_Buffer[0] / 50.0, 1.0);
   confidence += adx_strength * 0.4;
   
   //--- 2. EMA Alignment (30%)
   if(ArraySize(EMA_Fast_Buffer) > 0 && ArraySize(EMA_Slow_Buffer) > 0)
   {
      double ema_gap = MathAbs(EMA_Fast_Buffer[0] - EMA_Slow_Buffer[0]) / EMA_Slow_Buffer[0];
      double ema_score = MathMin(ema_gap * 100.0, 1.0);
      confidence += ema_score * 0.3;
   }
   
   //--- 3. ATR (volatility) (30%)
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ATR_Handle, 0, 0, 1, atr) > 0 && ArraySize(EMA_Slow_Buffer) > 0)
   {
      double atr_score = MathMin(1.0 - (atr[0] / (EMA_Slow_Buffer[0] * 0.02)), 1.0);
      confidence += MathMax(atr_score, 0.0) * 0.3;
   }
   
   return MathMin(MathMax(confidence, 0.0), 1.0);
}

//+------------------------------------------------------------------+
//| Draw Sniper Scope on chart                                       |
//+------------------------------------------------------------------+
void DrawSniperScope()
{
   if(!ScopeVisible) return;
   
   //--- Delete old scope objects
   DeleteScopeObjects();
   
   //--- Dynamic radius based on tension
   int dynamic_radius = ScopeRadius;
   if(CurrentTension > 0.3)
   {
      dynamic_radius = (int)(ScopeRadius * (1.0 - CurrentTension * 0.4));
      dynamic_radius = MathMax(dynamic_radius, ScopeRadius / 3);
   }
   
   //--- Scope color based on tension
   color scope_color = GetTensionColor(CurrentTension);
   
   //--- Create outer circle
   string name_outer = ObjPrefix + "Scope_Outer";
   ObjectCreate(0, name_outer, OBJ_ELLIPSE_BY_ANGLE, 0, 0, 0);
   ObjectSetInteger(0, name_outer, OBJPROP_COLOR, scope_color);
   ObjectSetInteger(0, name_outer, OBJPROP_WIDTH, ScopeThickness);
   ObjectSetInteger(0, name_outer, OBJPROP_STYLE, STYLE_SOLID);
   ObjectSetInteger(0, name_outer, OBJPROP_BACK, false);
   ObjectSetInteger(0, name_outer, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, name_outer, OBJPROP_XDISTANCE, ScopeCenterX);
   ObjectSetInteger(0, name_outer, OBJPROP_YDISTANCE, ScopeCenterY);
   ObjectSetDouble(0, name_outer, OBJPROP_ANGLE, 0);
   ObjectSetDouble(0, name_outer, OBJPROP_DEVIATION, 360);
   ObjectSetInteger(0, name_outer, OBJPROP_ELLIPSE_WIDTH, dynamic_radius);
   ObjectSetInteger(0, name_outer, OBJPROP_ELLIPSE_HEIGHT, dynamic_radius);
   
   //--- Create inner circle (2/3 of outer)
   int inner_radius = dynamic_radius * 2 / 3;
   string name_inner = ObjPrefix + "Scope_Inner";
   ObjectCreate(0, name_inner, OBJ_ELLIPSE_BY_ANGLE, 0, 0, 0);
   ObjectSetInteger(0, name_inner, OBJPROP_COLOR, scope_color);
   ObjectSetInteger(0, name_inner, OBJPROP_WIDTH, ScopeThickness);
   ObjectSetInteger(0, name_inner, OBJPROP_STYLE, STYLE_SOLID);
   ObjectSetInteger(0, name_inner, OBJPROP_BACK, false);
   ObjectSetInteger(0, name_inner, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, name_inner, OBJPROP_XDISTANCE, ScopeCenterX);
   ObjectSetInteger(0, name_inner, OBJPROP_YDISTANCE, ScopeCenterY);
   ObjectSetDouble(0, name_inner, OBJPROP_ANGLE, 0);
   ObjectSetDouble(0, name_inner, OBJPROP_DEVIATION, 360);
   ObjectSetInteger(0, name_inner, OBJPROP_ELLIPSE_WIDTH, inner_radius);
   ObjectSetInteger(0, name_inner, OBJPROP_ELLIPSE_HEIGHT, inner_radius);
   
   //--- Create crosshairs
   CreateCrosshair(scope_color);
   
   //--- Kill Zone (if tension is high)
   if(ShowKillZone && CurrentTension >= TensionThreshold)
   {
      KillZoneRadius = dynamic_radius / 2;
      string name_kill = ObjPrefix + "KillZone";
      ObjectCreate(0, name_kill, OBJ_ELLIPSE_BY_ANGLE, 0, 0, 0);
      ObjectSetInteger(0, name_kill, OBJPROP_COLOR, clrRed);
      ObjectSetInteger(0, name_kill, OBJPROP_WIDTH, ScopeThickness + 1);
      ObjectSetInteger(0, name_kill, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name_kill, OBJPROP_BACK, false);
      ObjectSetInteger(0, name_kill, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, name_kill, OBJPROP_XDISTANCE, ScopeCenterX);
      ObjectSetInteger(0, name_kill, OBJPROP_YDISTANCE, ScopeCenterY);
      ObjectSetDouble(0, name_kill, OBJPROP_ANGLE, 0);
      ObjectSetDouble(0, name_kill, OBJPROP_DEVIATION, 360);
      ObjectSetInteger(0, name_kill, OBJPROP_ELLIPSE_WIDTH, KillZoneRadius);
      ObjectSetInteger(0, name_kill, OBJPROP_ELLIPSE_HEIGHT, KillZoneRadius);
      
      //--- Kill Zone Text
      CreateLabel(ObjPrefix + "KillText", ScopeCenterX - 35, ScopeCenterY - 10, 
                  "KILL ZONE", 9, clrRed);
   }
   
   ChartRedraw();
}

//+------------------------------------------------------------------+
//| Create crosshair lines                                           |
//+------------------------------------------------------------------+
void CreateCrosshair(color clr)
{
   long chart_id = ChartID();
   int width = (int)ChartGetInteger(chart_id, CHART_WIDTH_IN_PIXELS);
   int height = (int)ChartGetInteger(chart_id, CHART_HEIGHT_IN_PIXELS);
   
   //--- Horizontal line
   string name_h = ObjPrefix + "Crosshair_H";
   ObjectCreate(0, name_h, OBJ_HLINE, 0, 0, 0);
   ObjectSetInteger(0, name_h, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name_h, OBJPROP_WIDTH, 1);
   ObjectSetInteger(0, name_h, OBJPROP_STYLE, STYLE_DOT);
   ObjectSetInteger(0, name_h, OBJPROP_BACK, true);
   ObjectSetInteger(0, name_h, OBJPROP_SELECTABLE, false);
   
   //--- Vertical line (approximation using trend line)
   string name_v = ObjPrefix + "Crosshair_V";
   ObjectCreate(0, name_v, OBJ_VLINE, 0, iTime(_Symbol, PERIOD_CURRENT, 0), 0);
   ObjectSetInteger(0, name_v, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name_v, OBJPROP_WIDTH, 1);
   ObjectSetInteger(0, name_v, OBJPROP_STYLE, STYLE_DOT);
   ObjectSetInteger(0, name_v, OBJPROP_BACK, true);
   ObjectSetInteger(0, name_v, OBJPROP_SELECTABLE, false);
}

//+------------------------------------------------------------------+
//| Delete all scope objects                                         |
//+------------------------------------------------------------------+
void DeleteScopeObjects()
{
   for(int i = ObjectsTotal(0) - 1; i >= 0; i--)
   {
      string name = ObjectName(0, i);
      if(StringFind(name, ObjPrefix + "Scope") == 0 || 
         StringFind(name, ObjPrefix + "Kill") == 0 ||
         StringFind(name, ObjPrefix + "Crosshair") == 0)
      {
         ObjectDelete(0, name);
      }
   }
}

//+------------------------------------------------------------------+
//| Get color based on tension level                                 |
//+------------------------------------------------------------------+
color GetTensionColor(double tension)
{
   if(tension < 0.3) return clrGray;
   if(tension < 0.5) return clrYellow;
   if(tension < 0.7) return clrOrange;
   return clrRed;
}

//+------------------------------------------------------------------+
//| Create Info Panel                                                |
//+------------------------------------------------------------------+
void CreateInfoPanel()
{
   int x = PanelX;
   int y = PanelY;
   int line_h = FontSize + 8;
   
   //--- Title
   CreateLabel(ObjPrefix + "Title", x, y, "🐝 SWARNE! ULTIMATE", FontSize + 4, clrYellow);
   y += line_h + 10;
   
   //--- Separator
   CreateLabel(ObjPrefix + "Sep1", x, y, "═══════════════════════", FontSize - 2, clrGray);
   y += line_h;
   
   //--- Price
   CreateLabel(ObjPrefix + "PriceLabel", x, y, "PRICE:", FontSize, clrWhite);
   CreateLabel(ObjPrefix + "PriceValue", x + 120, y, "----", FontSize + 1, clrYellow);
   y += line_h;
   
   //--- EMA
   CreateLabel(ObjPrefix + "EMA9Label", x, y, "EMA 9:", FontSize, clrDodgerBlue);
   CreateLabel(ObjPrefix + "EMA9Value", x + 120, y, "----", FontSize, clrDodgerBlue);
   y += line_h;
   
   CreateLabel(ObjPrefix + "EMA21Label", x, y, "EMA 21:", FontSize, clrRed);
   CreateLabel(ObjPrefix + "EMA21Value", x + 120, y, "----", FontSize, clrRed);
   y += line_h;
   
   //--- ADX
   CreateLabel(ObjPrefix + "ADXLabel", x, y, "ADX:", FontSize, clrWhite);
   CreateLabel(ObjPrefix + "ADXValue", x + 120, y, "----", FontSize, clrWhite);
   y += line_h + 5;
   
   //--- Separator
   CreateLabel(ObjPrefix + "Sep2", x, y, "═══════════════════════", FontSize - 2, clrGray);
   y += line_h;
   
   //--- Tension
   CreateLabel(ObjPrefix + "TensionLabel", x, y, "TENSION:", FontSize + 1, clrWhite);
   CreateLabel(ObjPrefix + "TensionValue", x + 120, y, "0%", FontSize + 1, clrWhite);
   y += line_h;
   
   //--- Confidence
   CreateLabel(ObjPrefix + "ConfLabel", x, y, "CONFIDENCE:", FontSize + 1, clrWhite);
   CreateLabel(ObjPrefix + "ConfValue", x + 120, y, "0%", FontSize + 1, clrWhite);
   y += line_h + 5;
   
   //--- Separator
   CreateLabel(ObjPrefix + "Sep3", x, y, "═══════════════════════", FontSize - 2, clrGray);
   y += line_h + 5;
   
   //--- Signal
   CreateLabel(ObjPrefix + "SignalLabel", x, y, "SIGNAL:", FontSize + 3, clrWhite);
   y += line_h + 5;
   CreateLabel(ObjPrefix + "SignalValue", x, y, "WAIT", FontSize + 6, clrOrange);
   
   ChartRedraw();
}

//+------------------------------------------------------------------+
//| Update Info Panel                                                |
//+------------------------------------------------------------------+
void UpdateInfoPanel(double price)
{
   //--- Update price
   UpdateLabel(ObjPrefix + "PriceValue", DoubleToString(price, _Digits), clrYellow);
   
   //--- Update EMA
   if(ArraySize(EMA_Fast_Buffer) > 0 && ArraySize(EMA_Slow_Buffer) > 0)
   {
      UpdateLabel(ObjPrefix + "EMA9Value", DoubleToString(EMA_Fast_Buffer[0], _Digits), clrDodgerBlue);
      UpdateLabel(ObjPrefix + "EMA21Value", DoubleToString(EMA_Slow_Buffer[0], _Digits), clrRed);
   }
   
   //--- Update ADX
   if(ArraySize(ADX_Buffer) > 0)
   {
      color adx_color = (ADX_Buffer[0] > InpADX_Threshold) ? clrLime : clrOrange;
      UpdateLabel(ObjPrefix + "ADXValue", DoubleToString(ADX_Buffer[0], 2), adx_color);
   }
   
   //--- Update Tension
   color tension_color = GetTensionColor(CurrentTension);
   UpdateLabel(ObjPrefix + "TensionValue", IntegerToString((int)(CurrentTension * 100)) + "%", tension_color);
   
   //--- Update Confidence
   color conf_color = (CurrentConfidence > 0.6) ? clrLime : (CurrentConfidence > 0.4) ? clrYellow : clrOrange;
   UpdateLabel(ObjPrefix + "ConfValue", IntegerToString((int)(CurrentConfidence * 100)) + "%", conf_color);
   
   //--- Update Signal
   string signal_text = "WAIT";
   color signal_color = clrOrange;
   
   if(CurrentTension >= TensionThreshold && CurrentConfidence > 0.5)
   {
      if(CurrentSignal == "BUY")
      {
         signal_text = BlinkState ? "🔥 BUY! 🔥" : "BUY NOW";
         signal_color = clrLime;
      }
      else if(CurrentSignal == "SELL")
      {
         signal_text = BlinkState ? "🔥 SELL! 🔥" : "SELL NOW";
         signal_color = clrRed;
      }
   }
   else if(ArraySize(EMA_Fast_Buffer) > 0 && ArraySize(EMA_Slow_Buffer) > 0)
   {
      if(EMA_Fast_Buffer[0] > EMA_Slow_Buffer[0])
      {
         signal_text = "BULLISH ↗";
         signal_color = clrLimeGreen;
      }
      else if(EMA_Fast_Buffer[0] < EMA_Slow_Buffer[0])
      {
         signal_text = "BEARISH ↘";
         signal_color = clrCoral;
      }
   }
   
   UpdateLabel(ObjPrefix + "SignalValue", signal_text, signal_color);
   
   ChartRedraw();
}

//+------------------------------------------------------------------+
//| Create label helper function                                     |
//+------------------------------------------------------------------+
void CreateLabel(string name, int x, int y, string text, int font_size, color clr)
{
   ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
   ObjectSetString(0, name, OBJPROP_TEXT, text);
   ObjectSetString(0, name, OBJPROP_FONT, "Arial Bold");
   ObjectSetInteger(0, name, OBJPROP_FONTSIZE, font_size);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_BACK, false);
   ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, name, OBJPROP_HIDDEN, true);
}

//+------------------------------------------------------------------+
//| Update label helper function                                     |
//+------------------------------------------------------------------+
void UpdateLabel(string name, string text, color clr = -1)
{
   if(ObjectFind(0, name) >= 0)
   {
      ObjectSetString(0, name, OBJPROP_TEXT, text);
      if(clr != -1)
         ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   }
}

//+------------------------------------------------------------------+
//| Timer function                                                    |
//+------------------------------------------------------------------+
void OnTimer()
{
   BlinkState = !BlinkState;
   DrawSniperScope();
}

//+------------------------------------------------------------------+
//| Chart Event Handler                                              |
//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
{
   //--- SPACE key: Toggle scope visibility
   if(id == CHARTEVENT_KEYDOWN && lparam == 32)  // Space bar
   {
      ScopeVisible = !ScopeVisible;
      if(!ScopeVisible)
         DeleteScopeObjects();
      Print("🎯 Scope ", ScopeVisible ? "VISIBLE" : "HIDDEN");
   }
   
   //--- Click to move scope
   if(id == CHARTEVENT_CLICK && ScopeVisible)
   {
      ScopeCenterX = (int)lparam;
      ScopeCenterY = (int)dparam;
      Print("📍 Scope moved to X=", ScopeCenterX, " Y=", ScopeCenterY);
   }
}

//+------------------------------------------------------------------+
//| Deinitialization function                                        |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   
   //--- Delete all objects
   ObjectsDeleteAll(0, ObjPrefix);
   
   //--- Release indicator handles
   if(EMA_Fast_Handle != INVALID_HANDLE) IndicatorRelease(EMA_Fast_Handle);
   if(EMA_Slow_Handle != INVALID_HANDLE) IndicatorRelease(EMA_Slow_Handle);
   if(ADX_Handle != INVALID_HANDLE) IndicatorRelease(ADX_Handle);
   if(ATR_Handle != INVALID_HANDLE) IndicatorRelease(ATR_Handle);
   if(RSI_Handle != INVALID_HANDLE) IndicatorRelease(RSI_Handle);
   
   ChartRedraw();
   Print("✅ SWARNE! ULTIMATE V1 deinitialized");
}
//+------------------------------------------------------------------+
