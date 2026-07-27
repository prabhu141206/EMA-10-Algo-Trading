  # =========================================================
# VIRTUAL TRADE ENGINE (MINIMAL + STABLE VERSION)
# =========================================================

from options.symbol_builder import build_option_symbol
from alerts.telegram_alert import telegram_alert
from alerts.message_templates import trade_entry, option_entry_alert, option_exit_alert
from utils.time_utils import epoch_to_ist
from db.logger import db_logger
import time
from System.shutdown_manager import shutdown_manager

class VirtualTradeEngine:

    def __init__(self, option_ws, state_machine):
        """
        Engine handles ONLY:
        - Option trade execution
        - Entry
        - Exit
        - Trade reset

        It does NOT:
        ❌ Decide strategy
        ❌ Manage triggers
        ❌ Write SQL directly
        """

        self.option_ws = option_ws
        self.state_machine = state_machine

        # =====================================================
        # TRADE STATE
        # =====================================================

        self.trade_active = False

        self.direction = None
        self.symbol = None

        # =====================================================
        # INDEX DATA
        # =====================================================

        self.index_price = None

        # =====================================================
        # ENTRY DATA
        # =====================================================

        self.entry_price = None
        self.entry_time = None

        # =====================================================
        # RISK MANAGEMENT
        # =====================================================

        self.target = None
        self.sl = None

        # =====================================================
        # TRADE DETAILS
        # =====================================================

        self.lot_size = 65
        self.capital_required = None
        

        self.strategy_name = "EMA 10 Strategy"

        # =====================================================
        # LIVE OPTION DATA
        # =====================================================

        self.last_option_price = None

    # =====================================================
    # START TRADE (called from BreakoutWatcher)
    # =====================================================

    def start_trade(self, direction, breakout_price, candle_time):

        # Safety check
        if self.trade_active:
            print("[ENGINE] Trade already active - ignoring")
            return

        print("[DEBUG] START_TRADE()")

        # =====================================================
        # STORE TRADE INFORMATION
        # =====================================================

        self.direction = direction
        self.index_price = breakout_price

        # =====================================================
        # BUILD OPTION SYMBOL
        # =====================================================

        self.symbol = build_option_symbol(
            index_price=breakout_price,
            direction=direction
        )

        print(f"[ENGINE] Selected Symbol : {self.symbol}")

        # =====================================================
        # SUBSCRIBE OPTION WEBSOCKET
        # =====================================================

        self.option_ws.subscribe(
            symbol=self.symbol,
            engine=self
        )

        print(f"[ENGINE] Direction : {self.direction}")
        print(f"[ENGINE] Breakout Price : {self.index_price}")
        print(f"[ENGINE] Option Symbol : {self.symbol}")

    # =====================================================
    # OPTION TICK (called from OptionWebSocket)
    # =====================================================

    def on_option_tick(self, price, ts):

        if shutdown_manager.partial_shutdown_done:

            if shutdown_manager.is_force_exit_time():
                self.force_exit()
                return

        # Always keep the latest option price
        self.last_option_price = price

        # Safety
        if not self.direction:
            return

        # =====================================================
        # TRADE ENTRY
        # =====================================================

        if not self.trade_active:

            self.trade_active = True

            # -----------------------------
            # Store Entry Information
            # -----------------------------

            self.entry_price = price
            self.entry_time = epoch_to_ist(ts)

            # =====================================================
            # TARGET / STOP LOSS
            # =====================================================

            self.target = self.entry_price + 20
            self.sl = self.entry_price - 10

            # -----------------------------
            # Capital Required
            # -----------------------------

            self.capital_required = (
                self.entry_price * self.lot_size
            )

            print(f"[ENTRY] Option : {self.entry_price}")
            print(f"[TARGET] : {self.target}")
            print(f"[SL] : {self.sl}")

            # =====================================================
            # DATABASE LOGGING
            # =====================================================

            db_logger.log_paper_trade_entry(

                symbol=self.symbol,

                strategy_name=self.strategy_name,

                direction=self.direction,

                index_price=self.index_price,

                entry_price=self.entry_price,

                entry_time=self.entry_time,

                sl_price=self.sl,

                target_price=self.target,

                lot_size=self.lot_size,

                capital_used=self.capital_required
            )

            # =====================================================
            # TELEGRAM ALERT
            # =====================================================

            telegram_alert.send(

                option_entry_alert(

                    symbol=self.symbol,

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

                    capital=self.capital_required,

                    target=self.target,

                    sl=self.sl,

                    time=self.entry_time
                )
            )

            return

        # =====================================================
        # EXIT CHECK
        # =====================================================

        if price >= self.target:

            self._exit_trade("TARGET", price)

        elif price <= self.sl:

            self._exit_trade("SL", price)



    # =====================================================
    # FORCE EXIT (Called by ShutdownManager)
    # =====================================================

    def force_exit(self):

        # No active trade
        if not self.trade_active:
            return

        # Safety
        if self.last_option_price is None:
            print("[ENGINE] Force exit failed: No option price available.")
            return

        print("[SHUTDOWN] Market closed. Initiating forced trade exit...")

        self._exit_trade(
            reason="FORCED_MARKET_CLOSE",
            price=self.last_option_price
        )



    # =====================================================
    # EXIT TRADE
    # =====================================================

    def _exit_trade(self, reason, price):

        # Safety
        if not self.trade_active:
            return

        print(f"[EXIT] {reason} @ {price}")

        # =====================================================
        # CALCULATE TRADE RESULT
        # =====================================================

        exit_time = epoch_to_ist(time.time())

        pnl = (price - self.entry_price) * self.lot_size

        if pnl >= 0:
            outcome = "Profit"
        else:
            outcome = "Loss"

        # =====================================================
        # STOP OPTION DATA
        # =====================================================

        self.trade_active = False

        self.option_ws.unsubscribe()

        # =====================================================
        # DATABASE LOGGING
        # =====================================================

        db_logger.log_paper_trade_exit(

            symbol=self.symbol,

            exit_price=price,

            exit_time=exit_time,

            pnl=pnl,

            exit_reason=reason
        )

        # =====================================================
        # TELEGRAM ALERT
        # =====================================================

        telegram_alert.send(

            option_exit_alert(

                symbol=self.symbol,

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

                pnl=pnl,

                reason=reason,

                outcome=outcome,

                time=exit_time
            )
        )

        # =====================================================
        # RESET STRATEGY
        # =====================================================

        self.state_machine.reset()

        # =====================================================
        # RESET ENGINE
        # =====================================================

        self._reset_internal()

        # =====================================================
        # FUTURE
        # =====================================================
        if shutdown_manager.check_market_close():
            shutdown_manager.evaluate_strategy_state()

        

    # =====================================================
    # INTERNAL RESET
    # =====================================================

    def _reset_internal(self):

        self.direction = None
        self.symbol = None
        self.entry_price = None
        self.target = None
        self.sl = None