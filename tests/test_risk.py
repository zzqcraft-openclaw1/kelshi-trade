from kelshi_trade.risk.rules import RiskLimits, check_order_allowed


def test_check_order_allowed_respects_resulting_position_size() -> None:
    limits = RiskLimits(max_position_size=2)
    assert check_order_allowed(current_size=0, order_size=1, side="BUY", limits=limits) is True
    assert check_order_allowed(current_size=1, order_size=1, side="BUY", limits=limits) is True
    assert check_order_allowed(current_size=2, order_size=1, side="BUY", limits=limits) is False
