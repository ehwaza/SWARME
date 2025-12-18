//+------------------------------------------------------------------+
//|                                        SWARNE_ULTIMATE_V1.mq5    |
//|                    SNIPER SCOPE + GOLDENEYE - VERSION CORRIGÉE   |
//|                                    Mathieu - Swarne! Project     |
//+------------------------------------------------------------------+
#property copyright "Mathieu - Swarne! Ultimate"
#property link      "https://github.com/swarne"
#property version   "1.01"
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
int KillZoneRadius = 0;
string ObjPrefix = "SWARNE_";

//--- Mouse tracking
bool MouseTrackingMode = false;
int LastMouseX = 0;
int LastMouseY = 0;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                          |
//+------------------------------------------------------------------+
int OnInit()
{
   //--- Indicator buffers mapping
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
   
   //--- Set arrays as series
   ArraySetAsSeries(EMA_Fast_Buffer, true);
   ArraySetAsSeries(EMA_Slow_Buffer, true);
   ArraySetAsSeries(BUY_Signal_Buffer, true);
   ArraySetAsSeries(SELL_Signal_Buffer, true);
   ArraySetAsSeries(StopLoss_Buffer, true);
   ArraySetAsSeries(TakeProfit_Buffer, true);
   ArraySetAsSeries(Tension_Buffer, true);
   ArraySetAsSeries(Confidence_Buffer, true);
   ArraySetAsSeries(RiskScore_Buffer, true);
   ArraySetAsSeries(ADX_Buffer, true);
   
   //--- Set arrow codes
   PlotIndexSetInteger(2, PLOT_ARROW, 233); // Up arrow
   PlotIndexSetInteger(3, PLOT_ARROW, 234); // Down arrow
   
   //--- Create indicators
   EMA_Fast_Handle = iMA(_Symbol, PERIOD_CURRENT, InpEMA_Fast, 0, MODE_EMA, PRICE_CLOSE);
   EMA_Slow_Handle = iMA(_Symbol, PERIOD_CURRENT, InpEMA_Slow, 0, MODE_EMA, PRICE_CLOSE);
   ADX_Handle = iADX(_Symbol, PERIOD_CURRENT, InpADX_Period);
   ATR_Handle = iATR(_Symbol, PERIOD_CURRENT, 14);
   RSI_Handle = iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE);
   
   //--- Check handles
   if(EMA_Fast_Handle == INVALID_HANDLE || EMA_Slow_Handle == INVALID_HANDLE ||
      ADX_Handle == INVALID_HANDLE || ATR_Handle == INVALID_HANDLE || RSI_Handle == INVALID_HANDLE)
   {
      Print("❌ Error creating indicators!");
      return(INIT_FAILED);
   }
   
   //--- Set timer for scope updates
   EventSetTimer(1);
   
   //--- Initial scope drawing
   DrawSniperScope();
   
   Print("🛡️ SWARNE ULTIMATE V1 - Initialized Successfully!");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                        |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   //--- Kill timer
   EventKillTimer();
   
   //--- Delete all scope objects
   DeleteScopeObjects();
   
   //--- Release indicator handles
   if(EMA_Fast_Handle != INVALID_HANDLE) IndicatorRelease(EMA_Fast_Handle);
   if(EMA_Slow_Handle != INVALID_HANDLE) IndicatorRelease(EMA_Slow_Handle);
   if(ADX_Handle != INVALID_HANDLE) IndicatorRelease(ADX_Handle);
   if(ATR_Handle != INVALID_HANDLE) IndicatorRelease(ATR_Handle);
   if(RSI_Handle != INVALID_HANDLE) IndicatorRelease(RSI_Handle);
   
   Print("🛡️ SWARNE ULTIMATE V1 - Deinitialized");
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
   if(rates_total < InpEMA_Slow + 10) return(0);
   
   //--- Set arrays as series
   ArraySetAsSeries(time, true);
   ArraySetAsSeries(close, true);
   ArraySetAsSeries(high, true);
   ArraySetAsSeries(low, true);
   
   int limit = rates_total - prev_calculated;
   if(limit > 1) limit = rates_total - 10;
   
   //--- Copy indicator data
   if(CopyBuffer(EMA_Fast_Handle, 0, 0, limit, EMA_Fast_Buffer) <= 0) return(0);
   if(CopyBuffer(EMA_Slow_Handle, 0, 0, limit, EMA_Slow_Buffer) <= 0) return(0);
   if(CopyBuffer(ADX_Handle, 0, 0, limit, ADX_Buffer) <= 0) return(0);
   
   //--- Calculate signals, tension, confidence
   for(int i = limit - 1; i >= 0; i--)
   {
      //--- Initialize
      BUY_Signal_Buffer[i] = EMPTY_VALUE;
      SELL_Signal_Buffer[i] = EMPTY_VALUE;
      StopLoss_Buffer[i] = EMPTY_VALUE;
      TakeProfit_Buffer[i] = EMPTY_VALUE;
      
      if(i < 2) continue;
      
      //--- Calculate Tension
      Tension_Buffer[i] = CalculateTension(i);
      
      //--- Calculate Confidence
      Confidence_Buffer[i] = CalculateConfidence(i);
      
      //--- Detect crossover signals
      bool ema_cross_up = (EMA_Fast_Buffer[i] > EMA_Slow_Buffer[i] && 
                          EMA_Fast_Buffer[i+1] <= EMA_Slow_Buffer[i+1]);
      bool ema_cross_down = (EMA_Fast_Buffer[i] < EMA_Slow_Buffer[i] && 
                            EMA_Fast_Buffer[i+1] >= EMA_Slow_Buffer[i+1]);
      
      //--- Check conditions
      bool adx_ok = ADX_Buffer[i] > InpADX_Threshold;
      bool tension_ok = Tension_Buffer[i] >= TensionThreshold;
      bool confidence_ok = Confidence_Buffer[i] >= 0.5;
      
      //--- Generate signals
      if(ema_cross_up && adx_ok && tension_ok && confidence_ok)
      {
         BUY_Signal_Buffer[i] = low[i] - 10 * _Point;
         
         //--- Calculate Stop Loss and Take Profit
         double atr[];
         ArraySetAsSeries(atr, true);
         if(CopyBuffer(ATR_Handle, 0, i, 1, atr) > 0)
         {
            StopLoss_Buffer[i] = close[i] - StopLossATR * atr[0];
            TakeProfit_Buffer[i] = close[i] + TakeProfitATR * atr[0];
         }
         
         if(ShowAlerts && i == 0)
         {
            Alert("🎯 SWARNE BUY SIGNAL at ", close[i]);
         }
      }
      else if(ema_cross_down && adx_ok && tension_ok && confidence_ok)
      {
         SELL_Signal_Buffer[i] = high[i] + 10 * _Point;
         
         //--- Calculate Stop Loss and Take Profit
         double atr[];
         ArraySetAsSeries(atr, true);
         if(CopyBuffer(ATR_Handle, 0, i, 1, atr) > 0)
         {
            StopLoss_Buffer[i] = close[i] + StopLossATR * atr[0];
            TakeProfit_Buffer[i] = close[i] - TakeProfitATR * atr[0];
         }
         
         if(ShowAlerts && i == 0)
         {
            Alert("🎯 SWARNE SELL SIGNAL at ", close[i]);
         }
      }
   }
   
   //--- Update current values
   if(rates_total > 0)
   {
      CurrentTension = Tension_Buffer[0];
      CurrentConfidence = Confidence_Buffer[0];
      
      if(BUY_Signal_Buffer[0] != EMPTY_VALUE)
         CurrentSignal = "BUY";
      else if(SELL_Signal_Buffer[0] != EMPTY_VALUE)
         CurrentSignal = "SELL";
      else
         CurrentSignal = "WAIT";
   }
   
   return(rates_total);
}

//+------------------------------------------------------------------+
//| Timer function                                                    |
//+------------------------------------------------------------------+
void OnTimer()
{
   //--- Update scope
   DrawSniperScope();
   
   //--- Update panel
   if(ShowPanel)
   {
      UpdateInfoPanel();
   }
   
   //--- Blink state for signals
   BlinkState = !BlinkState;
}

//+------------------------------------------------------------------+
//| Chart event function                                              |
//+------------------------------------------------------------------+
void OnChartEvent(const int id,
                  const long &lparam,
                  const double &dparam,
                  const string &sparam)
{
   if(id == CHARTEVENT_KEYDOWN)
   {
      //--- SPACE: Toggle scope visibility
      if(lparam == 32)
      {
         ScopeVisible = !ScopeVisible;
         if(!ScopeVisible)
            DeleteScopeObjects();
         else
            DrawSniperScope();
      }
      //--- M: Toggle mouse tracking
      else if(lparam == 77 || lparam == 109)
      {
         MouseTrackingMode = !MouseTrackingMode;
         string status = MouseTrackingMode ? "ON" : "OFF";
         Comment("🎯 Mouse Tracking: " + status);
      }
      //--- R: Manual refresh
      else if(lparam == 82 || lparam == 114)
      {
         DrawSniperScope();
      }
   }
   else if(id == CHARTEVENT_MOUSE_MOVE && MouseTrackingMode)
   {
      int x = (int)lparam;
      int y = (int)dparam;
      
      if(x != LastMouseX || y != LastMouseY)
      {
         ScopeCenterX = x;
         ScopeCenterY = y;
         LastMouseX = x;
         LastMouseY = y;
         DrawSniperScope();
      }
   }
   else if(id == CHARTEVENT_CLICK)
   {
      if(!MouseTrackingMode)
      {
         ScopeCenterX = (int)lparam;
         ScopeCenterY = (int)dparam;
         DrawSniperScope();
      }
   }
}

//+------------------------------------------------------------------+
//| Calculate Tension (0-1)                                           |
//+------------------------------------------------------------------+
double CalculateTension(int index)
{
   if(index < 2 || ArraySize(EMA_Fast_Buffer) <= index || ArraySize(EMA_Slow_Buffer) <= index)
      return 0.0;
   
   double tension = 0.0;
   
   //--- 1. EMA convergence (40%)
   double ema_distance = MathAbs(EMA_Fast_Buffer[index] - EMA_Slow_Buffer[index]);
   double avg_price = (EMA_Fast_Buffer[index] + EMA_Slow_Buffer[index]) / 2.0;
   double normalized_distance = (avg_price > 0) ? (ema_distance / avg_price) : 0.0;
   tension += (1.0 - MathMin(normalized_distance * 100.0, 1.0)) * 0.4;
   
   //--- 2. Recent crossover (30%)
   bool recent_cross = false;
   for(int i = 0; i < 5 && (index + i) < ArraySize(EMA_Fast_Buffer); i++)
   {
      if((EMA_Fast_Buffer[index + i] > EMA_Slow_Buffer[index + i] && 
          EMA_Fast_Buffer[index + i + 1] <= EMA_Slow_Buffer[index + i + 1]) ||
         (EMA_Fast_Buffer[index + i] < EMA_Slow_Buffer[index + i] && 
          EMA_Fast_Buffer[index + i + 1] >= EMA_Slow_Buffer[index + i + 1]))
      {
         recent_cross = true;
         break;
      }
   }
   if(recent_cross) tension += 0.3;
   
   //--- 3. RSI near 50 (30%)
   double rsi[];
   ArraySetAsSeries(rsi, true);
   if(CopyBuffer(RSI_Handle, 0, index, 1, rsi) > 0)
   {
      double rsi_neutrality = 1.0 - MathAbs(rsi[0] - 50.0) / 50.0;
      tension += rsi_neutrality * 0.3;
   }
   
   return MathMin(MathMax(tension, 0.0), 1.0);
}

//+------------------------------------------------------------------+
//| Calculate Confidence (0-1)                                        |
//+------------------------------------------------------------------+
double CalculateConfidence(int index)
{
   if(index < 2 || ArraySize(ADX_Buffer) <= index)
      return 0.0;
   
   double confidence = 0.0;
   
   //--- 1. ADX strength (40%)
   confidence += MathMin(ADX_Buffer[index] / 50.0, 1.0) * 0.4;
   
   //--- 2. EMA alignment (30%)
   if(ArraySize(EMA_Fast_Buffer) > index && ArraySize(EMA_Slow_Buffer) > index)
   {
      double ema_gap = MathAbs(EMA_Fast_Buffer[index] - EMA_Slow_Buffer[index]);
      double avg_price = (EMA_Fast_Buffer[index] + EMA_Slow_Buffer[index]) / 2.0;
      double gap_percent = (avg_price > 0) ? (ema_gap / avg_price) : 0.0;
      confidence += MathMin(gap_percent * 200.0, 1.0) * 0.3;
   }
   
   //--- 3. ATR (volatility) (30%)
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ATR_Handle, 0, index, 1, atr) > 0 && ArraySize(EMA_Slow_Buffer) > index)
   {
      double atr_score = MathMin(1.0 - (atr[0] / (EMA_Slow_Buffer[index] * 0.02)), 1.0);
      confidence += MathMax(atr_score, 0.0) * 0.3;
   }
   
   return MathMin(MathMax(confidence, 0.0), 1.0);
}

//+------------------------------------------------------------------+
//| ✅ CORRECTION: Draw Sniper Scope with valid MQL5 properties      |
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
   
   //--- ✅ CORRECTION: Use chart coordinates instead of pixel properties
   long chart_id = ChartID();
   
   //--- Convert pixel position to chart coordinates
   int x_pixel = ScopeCenterX;
   int y_pixel = ScopeCenterY;
   datetime time_center;
   double price_center;
   
   if(!ChartXYToTimePrice(chart_id, x_pixel, y_pixel, 0, time_center, price_center))
   {
      Print("❌ Error converting coordinates");
      return;
   }
   
   //--- Calculate time span for radius (proportional to pixels)
   int period_seconds = PeriodSeconds();
   datetime time_radius = time_center + period_seconds * (dynamic_radius / 10);
   
   //--- ✅ Create outer circle with TIME/PRICE coordinates
   string name_outer = ObjPrefix + "Scope_Outer";
   if(ObjectCreate(0, name_outer, OBJ_ELLIPSE_BY_ANGLE, 0, 
                   time_center, price_center,           // Center point
                   time_radius, price_center,           // Radius point
                   0, 360))                              // Full circle: 0-360 degrees
   {
      ObjectSetInteger(0, name_outer, OBJPROP_COLOR, scope_color);
      ObjectSetInteger(0, name_outer, OBJPROP_WIDTH, ScopeThickness);
      ObjectSetInteger(0, name_outer, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name_outer, OBJPROP_BACK, false);
      ObjectSetInteger(0, name_outer, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, name_outer, OBJPROP_FILL, false);
   }
   
   //--- ✅ Create inner circle (2/3 of outer)
   int inner_radius = dynamic_radius * 2 / 3;
   datetime time_inner = time_center + period_seconds * (inner_radius / 10);
   string name_inner = ObjPrefix + "Scope_Inner";
   
   if(ObjectCreate(0, name_inner, OBJ_ELLIPSE_BY_ANGLE, 0,
                   time_center, price_center,           // Center point
                   time_inner, price_center,            // Radius point  
                   0, 360))                              // Full circle
   {
      ObjectSetInteger(0, name_inner, OBJPROP_COLOR, scope_color);
      ObjectSetInteger(0, name_inner, OBJPROP_WIDTH, ScopeThickness);
      ObjectSetInteger(0, name_inner, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name_inner, OBJPROP_BACK, false);
      ObjectSetInteger(0, name_inner, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, name_inner, OBJPROP_FILL, false);
   }
   
   //--- Create crosshairs
   CreateCrosshair(scope_color);
   
   //--- ✅ Kill Zone (if tension is high)
   if(ShowKillZone && CurrentTension >= TensionThreshold)
   {
      KillZoneRadius = dynamic_radius / 2;
      datetime time_kill = time_center + period_seconds * (KillZoneRadius / 10);
      string name_kill = ObjPrefix + "KillZone";
      
      if(ObjectCreate(0, name_kill, OBJ_ELLIPSE_BY_ANGLE, 0,
                      time_center, price_center,        // Center point
                      time_kill, price_center,          // Radius point
                      0, 360))                           // Full circle
      {
         ObjectSetInteger(0, name_kill, OBJPROP_COLOR, clrRed);
         ObjectSetInteger(0, name_kill, OBJPROP_WIDTH, ScopeThickness + 1);
         ObjectSetInteger(0, name_kill, OBJPROP_STYLE, STYLE_SOLID);
         ObjectSetInteger(0, name_kill, OBJPROP_BACK, false);
         ObjectSetInteger(0, name_kill, OBJPROP_SELECTABLE, false);
         ObjectSetInteger(0, name_kill, OBJPROP_FILL, false);
      }
      
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
   string hline_name = ObjPrefix + "Crosshair_H";
   datetime time1, time2;
   double price_h;
   
   if(ChartXYToTimePrice(chart_id, 0, ScopeCenterY, 0, time1, price_h) &&
      ChartXYToTimePrice(chart_id, width, ScopeCenterY, 0, time2, price_h))
   {
      if(ObjectCreate(0, hline_name, OBJ_TREND, 0, time1, price_h, time2, price_h))
      {
         ObjectSetInteger(0, hline_name, OBJPROP_COLOR, clr);
         ObjectSetInteger(0, hline_name, OBJPROP_STYLE, STYLE_DOT);
         ObjectSetInteger(0, hline_name, OBJPROP_WIDTH, 1);
         ObjectSetInteger(0, hline_name, OBJPROP_BACK, false);
         ObjectSetInteger(0, hline_name, OBJPROP_SELECTABLE, false);
         ObjectSetInteger(0, hline_name, OBJPROP_RAY_RIGHT, false);
         ObjectSetInteger(0, hline_name, OBJPROP_RAY_LEFT, false);
      }
   }
   
   //--- Vertical line
   string vline_name = ObjPrefix + "Crosshair_V";
   datetime time_v;
   double price1, price2;
   
   if(ChartXYToTimePrice(chart_id, ScopeCenterX, 0, 0, time_v, price1) &&
      ChartXYToTimePrice(chart_id, ScopeCenterX, height, 0, time_v, price2))
   {
      if(ObjectCreate(0, vline_name, OBJ_TREND, 0, time_v, price1, time_v, price2))
      {
         ObjectSetInteger(0, vline_name, OBJPROP_COLOR, clr);
         ObjectSetInteger(0, vline_name, OBJPROP_STYLE, STYLE_DOT);
         ObjectSetInteger(0, vline_name, OBJPROP_WIDTH, 1);
         ObjectSetInteger(0, vline_name, OBJPROP_BACK, false);
         ObjectSetInteger(0, vline_name, OBJPROP_SELECTABLE, false);
         ObjectSetInteger(0, vline_name, OBJPROP_RAY_RIGHT, false);
         ObjectSetInteger(0, vline_name, OBJPROP_RAY_LEFT, false);
      }
   }
}

//+------------------------------------------------------------------+
//| Create label                                                      |
//+------------------------------------------------------------------+
void CreateLabel(string name, int x, int y, string text, int size, color clr)
{
   if(ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
      ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
      ObjectSetInteger(0, name, OBJPROP_FONTSIZE, size);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, name, OBJPROP_BACK, false);
      ObjectSetString(0, name, OBJPROP_TEXT, text);
      ObjectSetString(0, name, OBJPROP_FONT, "Arial Bold");
   }
}

//+------------------------------------------------------------------+
//| Update info panel                                                 |
//+------------------------------------------------------------------+
void UpdateInfoPanel()
{
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   
   //--- Title
   CreateLabel(ObjPrefix + "Title", PanelX, PanelY, 
               "🎯 SWARNE ULTIMATE", FontSize + 2, clrWhite);
   
   //--- Price
   string price_text = StringFormat("💰 Price: %.5f", bid);
   CreateLabel(ObjPrefix + "Price", PanelX, PanelY + 20, 
               price_text, FontSize, clrYellow);
   
   //--- EMAs
   if(ArraySize(EMA_Fast_Buffer) > 0 && ArraySize(EMA_Slow_Buffer) > 0)
   {
      string ema_text = StringFormat("📈 EMA: %.5f / %.5f", 
                                     EMA_Fast_Buffer[0], EMA_Slow_Buffer[0]);
      CreateLabel(ObjPrefix + "EMA", PanelX, PanelY + 40, 
                  ema_text, FontSize, clrDodgerBlue);
   }
   
   //--- ADX
   if(ArraySize(ADX_Buffer) > 0)
   {
      string adx_text = StringFormat("📊 ADX: %.1f", ADX_Buffer[0]);
      color adx_color = (ADX_Buffer[0] > InpADX_Threshold) ? clrLime : clrGray;
      CreateLabel(ObjPrefix + "ADX", PanelX, PanelY + 60, 
                  adx_text, FontSize, adx_color);
   }
   
   //--- Tension
   string tension_text = StringFormat("⚡ Tension: %.0f%%", CurrentTension * 100);
   color tension_color = GetTensionColor(CurrentTension);
   CreateLabel(ObjPrefix + "Tension", PanelX, PanelY + 80, 
               tension_text, FontSize, tension_color);
   
   //--- Confidence
   string conf_text = StringFormat("🎯 Confidence: %.0f%%", CurrentConfidence * 100);
   color conf_color = (CurrentConfidence >= 0.7) ? clrLime : 
                      (CurrentConfidence >= 0.5) ? clrYellow : clrGray;
   CreateLabel(ObjPrefix + "Confidence", PanelX, PanelY + 100, 
               conf_text, FontSize, conf_color);
   
   //--- Signal
   string signal_text = "🔔 " + CurrentSignal;
   color signal_color = (CurrentSignal == "BUY") ? clrLime :
                        (CurrentSignal == "SELL") ? clrRed : clrGray;
   
   //--- Blink for active signals
   if((CurrentSignal == "BUY" || CurrentSignal == "SELL") && BlinkState)
   {
      signal_text = "🔥 " + CurrentSignal + " 🔥";
   }
   
   CreateLabel(ObjPrefix + "Signal", PanelX, PanelY + 120, 
               signal_text, FontSize + 2, signal_color);
   
   //--- Stop Loss
   if(ArraySize(StopLoss_Buffer) > 0 && StopLoss_Buffer[0] != EMPTY_VALUE)
   {
      string sl_text = StringFormat("🛑 SL: %.5f", StopLoss_Buffer[0]);
      CreateLabel(ObjPrefix + "StopLoss", PanelX, PanelY + 145, 
                  sl_text, FontSize - 1, clrOrangeRed);
   }
   
   //--- Take Profit
   if(ArraySize(TakeProfit_Buffer) > 0 && TakeProfit_Buffer[0] != EMPTY_VALUE)
   {
      string tp_text = StringFormat("🎯 TP: %.5f", TakeProfit_Buffer[0]);
      CreateLabel(ObjPrefix + "TakeProfit", PanelX, PanelY + 165, 
                  tp_text, FontSize - 1, clrLimeGreen);
   }
}

//+------------------------------------------------------------------+
//| Get color based on tension level                                 |
//+------------------------------------------------------------------+
color GetTensionColor(double tension)
{
   if(tension < 0.3) return clrGray;
   else if(tension < 0.5) return clrYellow;
   else if(tension < 0.7) return clrOrange;
   else return clrRed;
}

//+------------------------------------------------------------------+
//| Delete all scope objects                                          |
//+------------------------------------------------------------------+
void DeleteScopeObjects()
{
   ObjectsDeleteAll(0, ObjPrefix);
   ChartRedraw();
}
//+------------------------------------------------------------------+
