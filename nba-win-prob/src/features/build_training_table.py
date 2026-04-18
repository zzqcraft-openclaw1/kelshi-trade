from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from .schema import CORE_ID_COLUMNS, TARGET_COLUMNS, ALL_FEATURE_COLUMNS


@dataclass
class TrainingTableBuilder:
    """Builds a leakage-safe pregame training table.

    Contract:
    - input rows must be sorted by game_date, then game_id
    - all derived features for a game must use only prior games
    - output is one row per scheduled game
    """

    rolling_windows: tuple[int, ...] = (5, 10)

    def build(self, team_games: pd.DataFrame, schedule: pd.DataFrame) -> pd.DataFrame:
        """Return a pregame training table.

        Expected future implementation steps:
        1. normalize raw team game stats
        2. compute team prior-to-game rolling aggregates
        3. join home-team pregame features
        4. join away-team pregame features
        5. compute differential features
        6. attach binary target: home_win
        7. validate leakage assumptions
        """
        self._validate_inputs(team_games=team_games, schedule=schedule)

        raise NotImplementedError(
            "Training table builder scaffold created, but feature generation is not implemented yet."
        )

    def _validate_inputs(self, team_games: pd.DataFrame, schedule: pd.DataFrame) -> None:
        required_team_game_columns = {
            "game_id",
            "game_date",
            "season",
            "team",
            "opponent",
            "is_home",
            "won",
        }
        required_schedule_columns = {
            "game_id",
            "game_date",
            "season",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
        }

        missing_team = required_team_game_columns - set(team_games.columns)
        missing_schedule = required_schedule_columns - set(schedule.columns)

        if missing_team:
            raise ValueError(f"team_games missing required columns: {sorted(missing_team)}")
        if missing_schedule:
            raise ValueError(f"schedule missing required columns: {sorted(missing_schedule)}")


def validate_training_table(df: pd.DataFrame) -> None:
    required_columns = set(CORE_ID_COLUMNS + TARGET_COLUMNS + ALL_FEATURE_COLUMNS)
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"training table missing required columns: {sorted(missing)}")
