# =========================================================
# MAIN ENTRYPOINT
# =========================================================


from System.startup_manger import StartupManager
from utils.Market_calender import market_status
import time

def main():


    

    # =====================================================
    # 1️⃣ WAIT FOR MARKET OPEN
    # =====================================================

    if not market_status.is_market_live():
    
        print(
            "\n🔔 Market Closed.\n"
            "Waiting for next trading session...\n"
        )
    
        current, next_open, seconds = (
            market_status.get_next_trading_session_info()
        )
    
        print(f"Current Time : {current}")
        print(f"Next Session : {next_open}")
        print(f"Waiting      : {seconds} sec\n")
    
        time.sleep(int(seconds))
    
    print(
        "\n🔔 Market Open."
        "\nStarting Trading System...\n"
    )

    startup = StartupManager()
    startup.start()
    startup.run()

# =========================================================
# PROGRAM ENTRYPOINT
# =========================================================

if __name__ == "__main__":
    main()