📈 EMA-10 Breakout Trading System (Paper Trading)

    A real-time, event-driven EMA-10 based breakout trading system built in Python.
    This project converts a manually traded price-action strategy into a rule-driven, automated paper-trading engine.

    The system listens to live market ticks, builds 5-minute candles, detects valid trigger candles based on EMA-10 conditions, and simulates trades with proper lifecycle management.

_____________________________________________________________________________________________________________________________________________________________________________



🔍 Strategy Overview

The strategy is based on EMA-10 (5-minute timeframe) and price action.

--------------------------------------------------BUY Setup----------------------------------------------------------

A BUY trigger candle is detected when:

    Price is above EMA-10
    Candle is red (pullback)
    Candle does NOT touch EMA-10
    Trigger price = High of the trigger candle
    Entry happens only if high breaks in the next candle

--------------------------------------------------SELL Setup----------------------------------------------------------

A SELL trigger candle is detected when:

    Price is below EMA-10
    Candle is green (pullback)
    Candle does NOT touch EMA-10
    Trigger price = Low of the trigger candle
    Entry happens only if low breaks in the next candle
    If no breakout happens in the very next candle, the trigger is expired.


This exactly mirrors manual discretionary trading, but with strict rules.



_________________________________________________________________________________________________________________________________________________________________________


⚙️ System Architecture

    The project is designed using clean separation of responsibilities.

        Live Ticks
        ↓
        Tick Handler
        ↓
        Candle Builder (5-min)
        ↓
        Signal Engine (EMA logic)
        ↓
        State Machine
        ↓
        Breakout Watcher
        ↓
        Paper Trade Engine

    Each component does only one job.


______________________________________________________________________________________________________________________________________________________________________________



🧠 Core Components Explained

candle_builder.py

    Converts tick-by-tick data into 5-minute OHLC candles
    Emits an event only when a candle closes
    Acts as the timing backbone of the system


signal_engine.py

    Evaluates only closed candles
    Applies EMA-10 logic
    Arms a trigger when conditions are met
    Does no trade execution


state_machine.py

Controls the entire lifecycle:

    IDLE
    TRIGGER_ARMED
    IN_TRADE

    This ensures:
        No double triggers
        No early expiry
        No overlapping trades
        breakout_watcher.py
        Watches live ticks after trigger
        Fires entry only on breakout

    Direction-aware (BUY / SELL)


paper_trade_engine.py

    Simulates trades without real money

    Manages:
        Entry price
        Stop-loss
        Target
        Exit conditions

    Logs every trade event separately


____________________________________________________________________________________________________________________________________________________________________________




📝 Logging & Transparency

Two types of logs are maintained:

    Trigger & Strategy Logs
    Trigger detected
    Trigger expired
    Entry fired
    Paper Trade Logs
    Entry
    Target hit
    Stop-loss hit
    Exit reason

All logs are stored as CSV files, making them easy to analyze later.


____________________________________________________________________________________________________________________________________________________________________________




🚀 Features:

    ✅ Real-time tick handling
    ✅ Accurate 5-minute candle construction
    ✅ No repainting logic
    ✅ Strict trigger → breakout → expire flow
    ✅ Parallel paper trading engine
    ✅ Clean console output for debugging
    ✅ Easily extendable to live trading


____________________________________________________________________________________________________________________________________________________________________________



⚠️ Disclaimer

This project is:

    For educational and research purposes only
    Not financial advice
    Uses paper trading only
    No real money execution is included
    Live trading requires:
    Broker risk checks
    Slippage handling
    Regulatory compliance


____________________________________________________________________________________________________________________________________________________________________________



🛠️ Tech Stack:

    Python – Core language for strategy, state management, and execution
    Fyers API (WebSocket & REST) – Live market data and broker connectivity
    Event-driven architecture – Tick → Candle → Signal → Trade flow
    CSV Logging – Transparent and auditable trade & strategy logs
    Modular system design – Clean separation of trading logic components

⚠️ Note:
    This project currently runs in paper trading mode only.
    Broker APIs are used only for market data, not live order placement.


____________________________________________________________________________________________________________________________________________________________________________




👤 Author

First-year Computer Engineering (CSE) student
ISBM College of Engineering, Pune
Currently pursuing Bachelor of Engineering (B.E.)

Actively working at the intersection of:

    Algorithmic Trading
    Market Microstructure
    System Design
    Backend Development

Background includes:

    Manual options and index trading
    Converting discretionary strategies into rule-based systems
    Building real-time trading engines using Python and broker APIs

This project reflects a learning-focused approach toward understanding how real-world trading systems are designed, tested, and validated before live deployment.


