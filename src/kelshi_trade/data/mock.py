from kelshi_trade.models import Market, Quote


class MockMarketDataSource:
    def list_markets(self) -> list[Market]:
        return [Market(market_id="demo", title="Demo market")]

    def get_quote(self, market_id: str) -> Quote:
        if market_id != "demo":
            raise KeyError(f"unknown market_id: {market_id}")
        return Quote(market_id="demo", bid=0.42, ask=0.46, last=0.41)
