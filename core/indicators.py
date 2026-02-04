class EMA:
    def __init__(self, period: int):
        self.period = period
        self.multiplier = 2 / (period + 1)
        self.value = None

    def update(self, close_price: float):
        """
        Call this ONLY on candle close.
        Returns current EMA value.
        """
        if self.value is None:
            # First EMA seed
            self.value = close_price
        else:
            self.value = (
                (close_price - self.value) * self.multiplier
                + self.value
            )
        return self.value


# ONE EMA INSTANCE (10-period)
ema_10 = EMA(period=10)
