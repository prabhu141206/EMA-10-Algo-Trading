# =========================================================
# VIRTUAL TRADE ENGINE (MINIMAL + STABLE VERSION)
# =========================================================

from options.symbol_builder import build_option_symbol


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

        # 🔴 CRITICAL: Symbol creation MUST exist
        self.symbol = build_option_symbol(
            index_price=spot_price,
            direction=direction
        )

        print(f"[ENGINE] Selected Symbol: {self.symbol}")

        # Subscribe to option ticks
        self.option_ws.subscribe(self.symbol, self)
        
        #testing 7
        print(f"[ENGINE] Start trade → {direction}")
        print(f"[ENGINE] Symbol → {self.symbol}")

    # =====================================================
    # OPTION TICK (called from OptionWebSocket)
    # =====================================================

    def on_option_tick(self, price, bid, ask, ts):

        # Ignore if direction not set (safety)
        if not self.direction:
            return

        # ================= ENTRY =================
        if not self.trade_active:

            # First tick = entry
            self.trade_active = True

            self.entry_price = price
            self.target = price + 20
            self.sl = price - 10

            # testing 9
            print(f"[ENTRY] Option @ {price}")
            print(f"[TARGET] {self.target} | [SL] {self.sl}")

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

        # 🔴 IMPORTANT: Reset strategy state
        self.state_machine.reset()

        # Reset engine variables
        self._reset_internal()

    # =====================================================
    # INTERNAL RESET
    # =====================================================

    def _reset_internal(self):

        self.direction = None
        self.symbol = None
        self.entry_price = None
        self.target = None
        self.sl = None