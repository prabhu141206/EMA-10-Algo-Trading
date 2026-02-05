from utils.logger import log_event
from utils.db_logger import db_logger

class StateMachine:
    def __init__(self):
        # States:
        # IDLE
        # TRIGGER_ARMED
        # IN_TRADE
        self.state = "IDLE"

        self.direction = None
        self.trigger_price = None
        self.trigger_time = None  # candle CLOSE time

        self.system_active = False

    # ================= SYSTEM =================

    def activate_system(self):
        self.system_active = True

    def is_system_active(self):
        return self.system_active

    # ================= TRIGGER =================

    def arm_trigger(self, direction, trigger_price, trigger_time):
        """
        Called ONLY on candle close
        """
        self.state = "TRIGGER_ARMED"
        self.direction = direction
        self.trigger_price = trigger_price
        self.trigger_time = trigger_time

        # ---------- CSV LOGGER ----------
        log_event(
            event_type="TRIGGER_ARMED",
            direction=direction,
            trigger_price=trigger_price,
            candle_time=trigger_time,
            note="Trigger candle detected"
        )

        # ---------- DATABASE LOGGER ----------
        db_logger.log_trade_event(
            event_type="TRIGGER_ARMED",
            direction=direction,
            price=trigger_price,
            trigger_price=trigger_price,
            candle_time=trigger_time,
            note="Trigger candle detected",
            ts=trigger_time
        )

    def is_trigger_armed(self):
        return self.state == "TRIGGER_ARMED"

    def expire_trigger(self):
        """
        Called ONLY on NEXT candle close
        """
        print("trigger is Expired\n")

        # ---------- CSV LOGGER ----------
        log_event(
            event_type="TRIGGER_EXPIRED",
            direction=self.direction,
            trigger_price=self.trigger_price,
            candle_time=self.trigger_time,
            note="No breakout in next candle"
        )

        # ---------- DATABASE LOGGER ----------
        db_logger.log_trade_event(
            event_type="TRIGGER_EXPIRED",
            direction=self.direction,
            price=self.trigger_price,
            trigger_price=self.trigger_price,
            candle_time=self.trigger_time,
            note="No breakout in next candle",
            ts=self.trigger_time
        )

        self.reset()

    # ================= TRADE =================

    def enter_trade(self):
        self.state = "IN_TRADE"

    def is_in_trade(self):
        return self.state == "IN_TRADE"

    # ================= RESET =================

    def reset(self):
        self.state = "IDLE"
        self.direction = None
        self.trigger_price = None
        self.trigger_time = None


state_machine = StateMachine()
