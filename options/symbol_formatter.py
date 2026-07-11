# =========================================================
# SYMBOL FORMATTER
# =========================================================
#
# Responsibility:
# - Convert broker symbol into readable format
#
# =========================================================

from expiry_selector import get_nearest_expiry


def format_symbol(raw_symbol: str):

    symbol = raw_symbol.replace("NSE:", "")

    expiry = get_nearest_expiry()

    expiry_str = expiry.strftime("%d %b %Y").upper()

    strike = symbol[-7:-2]

    option_type = (
        "CE"
        if symbol.endswith("CE")
        else "PE"
    )

    return (
        f"NIFTY "
        f"{expiry_str} "
        f"{strike} "
        f"{option_type}"
    )