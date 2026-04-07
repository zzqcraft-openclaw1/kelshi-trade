from kelshi_trade.models import Quote


def mean_reversion_signal(snapshot: Quote) -> str:
    mid = (snapshot.bid + snapshot.ask) / 2
    if snapshot.last < mid:
        return "BUY"
    if snapshot.last > mid:
        return "SELL"
    return "HOLD"
