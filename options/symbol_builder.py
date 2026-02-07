from .atm_selector import get_atm_strike
from .expiry_selector import get_nearest_expiry


def build_option_symbol(index_price: float, direction: str):
    atm = get_atm_strike(index_price)
    expiry = get_nearest_expiry()

    symbol = (
        f"NSE:NIFTY{expiry}{atm}CE"
        if direction == "BUY"
        else f"NSE:NIFTY{expiry}{atm}PE"
    )

    return symbol