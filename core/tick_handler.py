from core.candle_builder import candle_builder
from core.signal_engine import signal_engine
from core.state_machine import state_machine
from core.breakout_watcher import breakout_watcher
from core.paper_trade.paper_trade_engine import paper_trade_engine
from utils.time_utils import is_market_open, is_entry_allowed, epoch_to_ist
from datetime import timedelta


class TickHandler:
    def handle_tick(self, tick: dict):
        ts = tick["timestamp"]
        price = tick["price"]

        # 0️⃣ Ignore non-market ticks
        if not is_market_open(ts):
            return

        # 1️⃣ Always build candles
        candle_closed, closed_candle = candle_builder.add_tick(tick)

        # =================================================
        # 2️⃣ CANDLE CLOSE LOGIC (SINGLE SOURCE OF TRUTH)
        # =================================================
        if candle_closed:

            # 🔴 Expire previous trigger if exists
            if state_machine.is_trigger_armed():
                state_machine.expire_trigger()

            # 🔵 Evaluate new candle for trigger
            signal_engine.on_candle_close(closed_candle)

            # ✅ TIMEZONE SAFE PRINTING
            start = epoch_to_ist(closed_candle["timestamp"])
            end = start + timedelta(minutes=5)

            print(
                f"[CANDLE CLOSED] {start.strftime('%H:%M')} → {end.strftime('%H:%M')} |\n"
                f"Open={closed_candle['open']}\n"
                f"High={closed_candle['high']}\n"
                f"Low={closed_candle['low']}\n"
                f"Close={closed_candle['close']}\n"
                f"EMA_10={round(closed_candle['ema'], 2)}\n"
            )

            if state_machine.is_trigger_armed():
                print(
                    f"[TRIGGER] 🟡 Trigger candle detected "
                    f"({start.strftime('%H:%M')} → {end.strftime('%H:%M')})"
                )
            else:
                print("[INFO] ❌ No valid setup on this candle")

            return  # ⛔ nothing else on candle-close tick

        # =================================================
        # 3️⃣ TICK-BY-TICK BREAKOUT
        # =================================================
        if state_machine.is_trigger_armed() and is_entry_allowed(ts):
            breakout_watcher.check_tick(tick)

        # =================================================
        # 4️⃣ PAPER TRADE ENGINE (PARALLEL)
        # =================================================
        paper_trade_engine.on_index_tick(price,ts)


tick_handler = TickHandler()