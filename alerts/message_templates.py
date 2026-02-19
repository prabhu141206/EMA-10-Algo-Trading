"""
All Telegram Alert Message Templates
Professional Trading Alert Formatting
"""

# ==========================================================
# ✅ SYSTEM ALERTS
# ==========================================================

def system_start():
    return (
        "🤖 *EMA-10 Strategy Activated*\n\n"
        "📡 WebSocket Connected\n"
        "📊 Monitoring Live Market\n"
        "🟢 System Ready"
    )

def option_entry_alert(symbol, trend, instrument, 
entry_price, capital, target, sl, time):

    return f"""
            🚀 OPTION TRADE ENTRY

            Instrument : {symbol}
            Signal     : {trend}
            Action     : {instrument}

            Entry Price: ₹{entry_price:.2f}
            Capital Req: ₹{capital:.2f}

            Target     : ₹{target:.2f}
            Stoploss   : ₹{sl:.2f}

            Time       : {time}
        """

def system_stop():
    return (
        "🛑 *Strategy Stopped*\n\n"
        "📴 Market Monitoring Disabled"
    )


def websocket_reconnected():
    return (
        "🔄 *WebSocket Reconnected*\n\n"
        "📡 Data feed restored"
    )


# ==========================================================
# 🟡 TRIGGER ALERTS
# ==========================================================

def trigger_armed(direction, trigger_price, candle_time):
    return (
        "🟡 TRIGGER ARMED\n\n"
        f"📊 Direction : {direction}\n"
        f"🎯 Trigger Price : {trigger_price}\n"
        f"🕒 Candle Time : {candle_time}\n\n"
        "_Waiting for breakout confirmation..._"
    )


def trigger_expired(direction, trigger_price):
    return (
        "⚠️ TRIGGER EXPIRED\n\n"
        f"📊 Direction : {direction}\n"
        f"🎯 Trigger Price : {trigger_price}\n\n"
        "❌ No breakout occurred in next candle"
    )


# ==========================================================
# 🚀 ENTRY ALERTS
# ==========================================================

def trade_entry(direction, entry_price, sl_price, target_price, time):
    return (
        "🚀 TRADE ENTRY EXECUTED\n\n"
        f"📊 Direction : {direction}\n"
        f"💰 Entry Price : {entry_price}\n"
        f"📉 Stop Loss : {sl_price}\n"
        f"🎯 Target : {target_price}\n"
        f"🕒 Entry Time : {time}\n\n"
        "⚡ Breakout Confirmed"
    )


# ==========================================================
# 🏁 EXIT ALERTS
# ==========================================================

def trade_exit(direction, exit_price, pnl, reason, time):

    emoji = "🟢" if pnl > 0 else "🔴"

    return (
        f"{emoji} TRADE CLOSED\n\n"
        f"📊 Direction : {direction}\n"
        f"💰 Exit Price : {exit_price}\n"
        f"📈 PnL : {round(pnl, 2)}\n"
        f"📌 Exit Reason : {reason}\n"
        f"🕒 Exit Time : {time}"
    )


# ==========================================================
# 📊 PAPER TRADE ALERTS
# ==========================================================

def paper_trade_entry(direction, option_price, sl, target, delta):
    return (
        "🧪 *PAPER TRADE STARTED*\n\n"
        f"📊 Direction : `{direction}`\n"
        f"💰 Option Price : `{option_price}`\n"
        f"📉 Stop Loss : `{sl}`\n"
        f"🎯 Target : `{target}`\n"
        f"📐 Delta : `{delta}`"
    )


def paper_trade_exit(direction, exit_price, pnl, reason):
    return (
        "🧪 *PAPER TRADE CLOSED*\n\n"
        f"📊 Direction : `{direction}`\n"
        f"💰 Exit Price : `{exit_price}`\n"
        f"📈 PnL : `{round(pnl, 2)}`\n"
        f"📌 Reason : `{reason}`"
    )


# ==========================================================
# 📈 CANDLE / SIGNAL ALERTS
# ==========================================================

def candle_closed(start_time, end_time, open_, high_, low_, close_, ema):
    return (
        "🕯 *CANDLE CLOSED*\n\n"
        f"⏱ {start_time} → {end_time}\n\n"
        f"Open : `{open_}`\n"
        f"High : `{high_}`\n"
        f"Low  : `{low_}`\n"
        f"Close: `{close_}`\n"
        f"EMA-10 : `{round(ema, 2)}`"
    )


# ==========================================================
# 📉 RISK / WARNING ALERTS
# ==========================================================

def risk_warning(message):
    return (
        "⚠️ *RISK ALERT*\n\n"
        f"{message}"
    )


# ==========================================================
# ❌ ERROR ALERTS
# ==========================================================

def error_alert(error_message):
    return (
        "🚨 *SYSTEM ERROR*\n\n"
        f"{error_message}"
    )


# ==========================================================
# ❤️ HEARTBEAT / HEALTH CHECK
# ==========================================================

def heartbeat():
    return (
        "💓 *System Alive*\n"
        "Algo running normally"
    )


# ==========================================================
# 📊 DAILY SUMMARY ALERT
# ==========================================================

def daily_summary(total_trades, wins, losses, total_pnl):
    emoji = "🟢" if total_pnl > 0 else "🔴"

    return (
        f"{emoji} *DAILY PERFORMANCE REPORT*\n\n"
        f"📊 Total Trades : `{total_trades}`\n"
        f"✅ Wins : `{wins}`\n"
        f"❌ Losses : `{losses}`\n"
        f"💰 Net PnL : `{round(total_pnl, 2)}`"
    )


def option_exit_alert(symbol, trend, instrument, exit_price, pnl, reason, outcome, time):
    return f"""
        🚪 OPTION TRADE EXIT
        
        📊 Symbol: {symbol}
        📈 Trend: {trend}
        🎯 Instrument: {instrument}
        
        💰 Exit Price: {exit_price}
        📊 PnL: {round(pnl,2)}
        
        📌 Reason: {reason}
        ⚖️ Outcome: {outcome}
        ⏰ Time: {time}
        """
