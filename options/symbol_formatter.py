def format_symbol(raw_symbol: str):
    # NSE:NIFTY2621025600CE
    s = raw_symbol.replace("NSE:", "")

    strike = s[-7:-2]
    opt_type = "CE" if s.endswith("CE") else "PE"

    return f"NIFTY {strike} {opt_type}"