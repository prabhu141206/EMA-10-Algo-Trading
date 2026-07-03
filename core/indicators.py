





from tvDatafeed import TvDatafeed, Interval


class EMA:
    def __init__(
        self,
        symbol: str,
        exchange: str,
        period: int = 10,
        interval=Interval.in_5_minute,
        bars: int = 100
    ):
        self.period = period
        self.multiplier = 2 / (period + 1)
        self.value = None

        self._initialize_ema(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            bars=bars
        )

    def _initialize_ema(
        self,
        symbol,
        exchange,
        interval,
        bars
    ):
        """
        Fetch historical candles from TradingView
        and initialize the current EMA value.
        """
        tv = TvDatafeed()

        df = tv.get_hist(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            n_bars=bars
        )

        if df is None or df.empty:
            raise Exception("Unable to fetch historical data.")

        closes = df["close"].tolist()

        # Seed EMA with first close
        ema = closes[0]

        for close in closes[1:]:
            ema = (
                (close - ema) * self.multiplier
                + ema
            )

        self.value = ema

    def update(self, close_price: float):
        """
        Call this ONLY when a new candle closes.
        """
        self.value = (
            (close_price - self.value) * self.multiplier
            + self.value
        )
        return self.value

    def get_initial_value(self):
        return self.value
    



ema_10 = EMA(
    symbol="NIFTY",
    exchange="NSE",
    period=10,
    interval=Interval.in_5_minute,
    bars=100
)

#print("Initial EMA:", ema_10.get_initial_value())

# On every new candle close
#new_ema = ema_10.update(25135.60)
#print("Updated EMA:", new_ema)