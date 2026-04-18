from src.features.schema import ALL_FEATURE_COLUMNS, CORE_ID_COLUMNS, TARGET_COLUMNS


def test_schema_has_expected_sections():
    assert "game_id" in CORE_ID_COLUMNS
    assert "home_win" in TARGET_COLUMNS
    assert "diff_net_rating_last_10" in ALL_FEATURE_COLUMNS
