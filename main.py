import time

from system.Startup_manger import StartupManager
from utils.market_status import get_market_status
from utils.schedular import get_next_start_time

def main():

    while True:

        # =====================================================
        # CHECK MARKET STATUS
        # =====================================================

        is_live, waiting_seconds = get_market_status()

        # -----------------------------------------------------
        # MARKET NOT LIVE
        # -----------------------------------------------------

        if not is_live:

            # Market will open today
            if waiting_seconds > 0:

                print(f"[SYSTEM] Market not open.")
                print(f"[SYSTEM] Waiting {int(waiting_seconds)} seconds...\n")

                time.sleep(waiting_seconds)

                continue

            # Market already closed
            current, next_start, waiting_seconds = get_next_start_time()

            print(f"[SYSTEM] Trading session completed.")
            print(f"[SYSTEM] Current Time : {current}")
            print(f"[SYSTEM] Next Session : {next_start}")
            print(f"[SYSTEM] Waiting {int(waiting_seconds)} seconds...\n")

            time.sleep(waiting_seconds)

            continue

        # =====================================================
        # START TRADING SYSTEM
        # =====================================================

        print("[SYSTEM] Starting Trading System...\n")

        startup = StartupManager()
        startup.start()


if __name__ == "__main__":
    main()