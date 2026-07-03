from nse import NSE
from datetime import datetime,timedelta




class MarketCalendar:

    def __init__(self):
        self.today = datetime.now().weekday()  # Monday is 0 and Sunday is 6

        with NSE(download_folder="/tmp") as nse:     # Fetch market status using NSE API library
            self.segments = nse.status()

        # Get current date and time
        self.now = datetime.now()
        self.current_date = self.now.date()

        #  List of 2026 Indian Market Holidays (Weekdays only)
        self.holidays = [
            '2026-01-26', '2026-03-03', '2026-03-26', '2026-03-31', '2026-04-03',
            '2026-04-14', '2026-05-01', '2026-05-28', '2026-06-26', '2026-09-14',
            '2026-10-02', '2026-10-20', '2026-11-10', '2026-11-24', '2026-12-25'
        ]

    def is_market_live(self):

        for seg in self.segments:               # Check if the market is open for the "Capital Market" segment
            if seg["market"] == "Capital Market":
                return seg["marketStatus"] == "Open"
                
        return False

    def is_weekend(self):
        return self.today >= 5  # Saturday and Sunday are considered weekends
    
    def get_next_trading_session_info(self):

        # 1. Start checking from the current date (set in constructor)
        next_open_date = self.current_date

        # 2. Find the next valid trading day (Skip Weekends & Holidays)
        while True:
            is_holiday = next_open_date.strftime('%Y-%m-%d') in self.holidays
            # Use self.is_weekend(next_open_date) if your method takes an argument, 
            # or check directly: next_open_date.weekday() >= 5
            if next_open_date.weekday() >= 5 or is_holiday:
                next_open_date += timedelta(days=1)
            else:
                # Found a trading day
                break

        # --- CODE MUST BE OUTSIDE THE LOOP ---

        # 3. Set Market Open Time (09:15:00) on the found date
        market_open_dt = datetime.combine(next_open_date, datetime.min.time().replace(hour=9, minute=15, second=0))

        # 4. Edge Case: If market already opened today (current time > 09:15), move to NEXT trading day
        if market_open_dt <= self.now:
            next_open_date += timedelta(days=1)
            while True:
                is_holiday = next_open_date.strftime('%Y-%m-%d') in self.holidays
                if next_open_date.weekday() >= 5 or is_holiday:
                    next_open_date += timedelta(days=1)
                else:
                    break
            # Recalculate time for the new day
            market_open_dt = datetime.combine(next_open_date, datetime.min.time().replace(hour=9, minute=15, second=0))

        # 5. Calculate Seconds
        # Use self.now which was set in the constructor
        total_seconds = int((market_open_dt - self.now).total_seconds())

        # 6. Return Results
        time_str_now = self.now.strftime("%Y-%m-%d %H:%M:%S")
        time_str_open = market_open_dt.strftime("%Y-%m-%d %H:%M:%S")

        #7. to know current time is AM or PM
        if self.now.hour < 12:
            time_str_now += " AM"
        else:
            time_str_now += " PM"
        
        return time_str_now, time_str_open + " AM", total_seconds   


    

# initialize the MarketCalendar object to check market status and weekend
market_status = MarketCalendar()

#print(market_status.get_next_trading_session_info())
#print(market_status.is_market_live())