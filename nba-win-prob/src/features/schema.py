"""Feature schema for leakage-safe pregame NBA win probability modeling."""

CORE_ID_COLUMNS = [
    "game_id",
    "game_date",
    "season",
    "home_team",
    "away_team",
]

TARGET_COLUMNS = [
    "home_win",
]

PREGAME_FEATURE_COLUMNS = [
    "home_win_pct",
    "away_win_pct",
    "home_net_rating_last_5",
    "away_net_rating_last_5",
    "home_net_rating_last_10",
    "away_net_rating_last_10",
    "home_off_rating_last_10",
    "away_off_rating_last_10",
    "home_def_rating_last_10",
    "away_def_rating_last_10",
    "home_pace_last_10",
    "away_pace_last_10",
    "home_efg_pct_last_10",
    "away_efg_pct_last_10",
    "home_tov_pct_last_10",
    "away_tov_pct_last_10",
    "home_orb_pct_last_10",
    "away_orb_pct_last_10",
    "home_ft_rate_last_10",
    "away_ft_rate_last_10",
    "home_rest_days",
    "away_rest_days",
    "home_b2b",
    "away_b2b",
    "home_strength_of_schedule",
    "away_strength_of_schedule",
]

DIFF_FEATURE_COLUMNS = [
    "diff_win_pct",
    "diff_net_rating_last_5",
    "diff_net_rating_last_10",
    "diff_off_rating_last_10",
    "diff_def_rating_last_10",
    "diff_pace_last_10",
    "diff_efg_pct_last_10",
    "diff_tov_pct_last_10",
    "diff_orb_pct_last_10",
    "diff_ft_rate_last_10",
    "diff_rest_days",
    "diff_strength_of_schedule",
]

ALL_FEATURE_COLUMNS = PREGAME_FEATURE_COLUMNS + DIFF_FEATURE_COLUMNS
