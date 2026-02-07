class BaseEngine:
    def on_trigger(self, direction, spot_price, candle_time):
        raise NotImplementedError

    def on_option_tick(self, price, bid, ask, ts):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError