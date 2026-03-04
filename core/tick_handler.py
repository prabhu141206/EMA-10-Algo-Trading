from core.candle_builder import candle_builder
from core.signal_engine import signal_engine
from core.state_machine import state_machine
from utils.time_utils import is_market_open, is_entry_allowed, epoch_to_ist
from datetime import timedelta


class TickHandler:

    def __init__(self, breakout_watcher):
        self.breakout_watcher = breakout_watcher

    def handle_tick(self, tick: dict):

        ts = tick["timestamp"]

        if not is_market_open(ts):
            return

        candle_closed, closed_candle = candle_builder.add_tick(tick)

        # ============================
        # Candle close logic
        # ============================
        if candle_closed:

            if state_machine.is_trigger_armed():
                state_machine.expire_trigger()

            signal_engine.on_candle_close(closed_candle)

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

            return

        # ============================
        # Tick-by-tick breakout
        # ============================
        if state_machine.is_trigger_armed() and is_entry_allowed(ts):
            self.breakout_watcher.check_tick(tick)