# =========================================================
# OPTION SYMBOL BUILDER
# =========================================================
#
# Responsibility:
# - Build broker symbol
#
# =========================================================

from .atm_selector import get_atm_strike
from .expiry_selector import get_nearest_expiry


def build_option_symbol(index_price: float, direction: str):

    atm = get_atm_strike(index_price)

    expiry = get_nearest_expiry()

    # 14JUL26
    expiry_str = expiry.strftime("%d%b%y").upper()

    option_type = (
        "CE"
        if direction == "BUY"
        else "PE"
    )

    symbol = (
        f"NIFTY{expiry_str}{atm}{option_type}"
    )

    return symbol



#print(build_option_symbol(24039.10,"BUY"))