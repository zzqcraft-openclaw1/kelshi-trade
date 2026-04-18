import pandas as pd

from src.features.build_training_table import TrainingTableBuilder


def test_builder_creates_leakage_safe_training_table():
    team_games = pd.DataFrame(
        [
            {"game_id": 1, "game_date": "2024-01-01", "season": 2024, "team": "A", "opponent": "B", "is_home": 1, "won": 1, "points_for": 110, "points_against": 100, "possessions": 100, "efg_pct": 0.54, "tov_pct": 0.11, "orb_pct": 0.27, "ft_rate": 0.22, "opponent_win_pct": 0.50},
            {"game_id": 1, "game_date": "2024-01-01", "season": 2024, "team": "B", "opponent": "A", "is_home": 0, "won": 0, "points_for": 100, "points_against": 110, "possessions": 100, "efg_pct": 0.49, "tov_pct": 0.14, "orb_pct": 0.24, "ft_rate": 0.18, "opponent_win_pct": 0.50},
            {"game_id": 2, "game_date": "2024-01-03", "season": 2024, "team": "A", "opponent": "C", "is_home": 0, "won": 0, "points_for": 105, "points_against": 111, "possessions": 101, "efg_pct": 0.51, "tov_pct": 0.13, "orb_pct": 0.25, "ft_rate": 0.20, "opponent_win_pct": 0.55},
            {"game_id": 2, "game_date": "2024-01-03", "season": 2024, "team": "C", "opponent": "A", "is_home": 1, "won": 1, "points_for": 111, "points_against": 105, "possessions": 101, "efg_pct": 0.53, "tov_pct": 0.12, "orb_pct": 0.26, "ft_rate": 0.19, "opponent_win_pct": 0.50},
            {"game_id": 3, "game_date": "2024-01-05", "season": 2024, "team": "B", "opponent": "C", "is_home": 1, "won": 1, "points_for": 112, "points_against": 104, "possessions": 99, "efg_pct": 0.55, "tov_pct": 0.10, "orb_pct": 0.28, "ft_rate": 0.24, "opponent_win_pct": 0.55},
            {"game_id": 3, "game_date": "2024-01-05", "season": 2024, "team": "C", "opponent": "B", "is_home": 0, "won": 0, "points_for": 104, "points_against": 112, "possessions": 99, "efg_pct": 0.50, "tov_pct": 0.13, "orb_pct": 0.23, "ft_rate": 0.17, "opponent_win_pct": 0.00},
        ]
    )

    schedule = pd.DataFrame(
        [
            {"game_id": 1, "game_date": "2024-01-01", "season": 2024, "home_team": "A", "away_team": "B", "home_score": 110, "away_score": 100},
            {"game_id": 2, "game_date": "2024-01-03", "season": 2024, "home_team": "C", "away_team": "A", "home_score": 111, "away_score": 105},
            {"game_id": 3, "game_date": "2024-01-05", "season": 2024, "home_team": "B", "away_team": "C", "home_score": 112, "away_score": 104},
        ]
    )

    builder = TrainingTableBuilder()
    df = builder.build(team_games=team_games, schedule=schedule)

    assert len(df) == 3

    first_game = df[df["game_id"] == 1].iloc[0]
    assert first_game["home_win_pct"] == 0.5
    assert first_game["away_win_pct"] == 0.5

    third_game = df[df["game_id"] == 3].iloc[0]
    assert third_game["home_win_pct"] == 0.0
    assert third_game["away_win_pct"] == 1.0
    assert third_game["diff_win_pct"] == -1.0
