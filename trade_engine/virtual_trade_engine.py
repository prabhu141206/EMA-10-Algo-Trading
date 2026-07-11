  # =========================================================
# VIRTUAL TRADE ENGINE (MINIMAL + STABLE VERSION)
# =========================================================

from options.symbol_builder import build_option_symbol
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import trade_entry, option_entry_alert, option_exit_alert
from utils.time_utils import epoch_to_ist
import time
#from System.shutdown_manager import shutdown_manager

class VirtualTradeEngine:

    def __init__(self, option_ws, state_machine):
        """
        Engine handles ONLY:
        - symbol creation
        - entry
        - exit
        - reset

        It does NOT:
        ❌ decide strategy
        ❌ manage triggers
        ❌ send alerts
        ❌ write to DB
        """

        self.option_ws = option_ws
        self.state_machine = state_machine

        # Trade state
        self.trade_active = False
        self.direction = None
        self.symbol = None

        # Trade data
        self.entry_price = None
        self.target = None
        self.sl = None

    # =====================================================
    # START TRADE (called from BreakoutWatcher)
    # =====================================================

    def start_trade(self, direction, spot_price, candle_time):

        # Safety check
        if self.trade_active:
            print("[ENGINE] Trade already active — ignoring")
            return

        self.direction = direction
        print("[DEBUG 2] START_TRADE() entered")
        # 🔴 CRITICAL: Symbol creation MUST exist
        self.symbol = build_option_symbol(
            index_price=spot_price,
            direction=direction
        )

        # Subscribe to option ticks
        self.option_ws.subscribe(symbol=self.symbol, engine=self)

        print(f"[ENGINE] Selected Symbol: {self.symbol}")

        
        
        #testing 7
        print(f"[ENGINE] Start trade → {direction}")
        print(f"[ENGINE] Symbol → {self.symbol}")

    # =====================================================
    # OPTION TICK (called from OptionWebSocket)
    # =====================================================

    def on_option_tick(self, price,ts):

        # Ignore if direction not set (safety)
        if not self.direction:
            return

        # ================= ENTRY =================
        if not self.trade_active:
            
            # First tick = entry
            self.trade_active = True

            self.entry_price = price

            # =====================================
            # TARGET / SL
            # =====================================

            if self.direction == "BUY":

                self.target = (
                    self.entry_price + 20
                )

                self.sl = (
                    self.entry_price - 10
                )

            else:

                self.target = (
                    self.entry_price + 20
                )

                self.sl = (
                    self.entry_price - 10
                )

            # testing 9
            print(f"[ENTRY] Option @ {price}")
            print(f"[TARGET] {self.target} | [SL] {self.sl}")


            # =====================================
            # TELEGRAM ENTRY ALERT
            # =====================================

            capital_required = (
                self.entry_price * 65
            )

            telegram_alert.send(

                option_entry_alert(

                    symbol=self.option_symbol,

                    trend=(
                        "Upside Breakout"
                        if self.direction == "BUY"
                        else "Downside Breakout"
                    ),

                    instrument=(
                        "Buy Call Option"
                        if self.direction == "BUY"
                        else "Buy Put Option"
                    ),

                    entry_price=self.entry_price,

                    capital=capital_required,

                    target=self.target,

                    sl=self.sl,

                    time=epoch_to_ist(ts)
                )
            )

            return

        # ================= EXIT =================
        if price >= self.target:
            self._exit_trade("TARGET", price)

        elif price <= self.sl:
            self._exit_trade("SL", price)

    # =====================================================
    # EXIT TRADE
    # =====================================================

    def _exit_trade(self, reason, price):

        if not self.trade_active:
            return
        
        #testing 10
        print(f"[EXIT] {reason} @ {price}")

        # Reset trade flag
        self.trade_active = False

        # Unsubscribe option data
        self.option_ws.unsubscribe()

        # =====================================
        # TELEGRAM EXIT ALERT
        # =====================================

        telegram_alert.send(

            option_exit_alert(

                symbol=self.option_symbol,

                trend=(
                    "Upside Breakout"
                    if self.direction == "BUY"
                    else "Downside Breakout"
                ),

                instrument=(
                    "Buy Call Option"
                    if self.direction == "BUY"
                    else "Buy Put Option"
                ),

                exit_price=price,

                pnl=price,

                reason=reason,

                outcome=(
                    "Profit"
                    if price > 0
                    else "Loss"
                ),

                time=epoch_to_ist(time.time())
            )
        )

        

        # 🔴 IMPORTANT: Reset strategy state
        self.state_machine.reset()

        # Reset engine variables
        self._reset_internal()

        #Check if shutdown is pending

        

    # =====================================================
    # INTERNAL RESET
    # =====================================================

    def _reset_internal(self):

        self.direction = None
        self.symbol = None
        self.entry_price = None
        self.target = None
        self.sl = None