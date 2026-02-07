

def get_atm_strike(price: float, step: int = 50) -> int:     #(current step is 50 fro nifty 50)
    return round(price / step) * step


