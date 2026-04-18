from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .schema import ALL_FEATURE_COLUMNS, CORE_ID_COLUMNS, TARGET_COLUMNS


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
        """Return a leakage-safe pregame training table."""
        self._validate_inputs(team_games=team_games, schedule=schedule)

        team_games = self._prepare_team_games(team_games)
        schedule = self._prepare_schedule(schedule)

        pregame_features = self._compute_pregame_team_features(team_games)
        training_df = self._assemble_training_table(schedule, pregame_features)
        training_df = self._finalize_training_table(training_df)

        validate_training_table(training_df)
        return training_df

    def _prepare_team_games(self, team_games: pd.DataFrame) -> pd.DataFrame:
        df = team_games.copy()
        df["game_date"] = pd.to_datetime(df["game_date"], utc=True)
        df = df.sort_values(["team", "game_date", "game_id"]).reset_index(drop=True)

        numeric_defaults = {
            "points_for": 0.0,
            "points_against": 0.0,
            "possessions": 100.0,
            "efg_pct": 0.5,
            "tov_pct": 0.12,
            "orb_pct": 0.25,
            "ft_rate": 0.20,
            "opponent_win_pct": 0.5,
        }
        for column, default in numeric_defaults.items():
            if column not in df.columns:
                df[column] = default

        df["won"] = df["won"].astype(int)
        df["possessions"] = df["possessions"].replace(0, pd.NA).fillna(100.0)
        df["off_rating"] = 100.0 * df["points_for"] / df["possessions"]
        df["def_rating"] = 100.0 * df["points_against"] / df["possessions"]
        df["net_rating"] = df["off_rating"] - df["def_rating"]
        df["pace"] = df["possessions"]
        return df

    def _prepare_schedule(self, schedule: pd.DataFrame) -> pd.DataFrame:
        df = schedule.copy()
        df["game_date"] = pd.to_datetime(df["game_date"], utc=True)
        df = df.sort_values(["game_date", "game_id"]).reset_index(drop=True)
        df["home_win"] = (df["home_score"] > df["away_score"]).astype(int)
        return df

    def _compute_pregame_team_features(self, team_games: pd.DataFrame) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        for _, group in team_games.groupby("team", sort=False):
            frames.append(self._compute_team_history_features(group.copy()))
        return pd.concat(frames, ignore_index=True)

    def _compute_team_history_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(["game_date", "game_id"]).reset_index(drop=True)

        prior_games = pd.Series(range(len(df)), index=df.index)
        df["games_played_before"] = prior_games
        df["wins_before"] = df["won"].shift(1).fillna(0).cumsum()
        df["home_win_pct"] = (df["wins_before"] / df["games_played_before"].replace(0, pd.NA)).fillna(0.5)

        for window in self.rolling_windows:
            for source, output in [
                ("net_rating", f"net_rating_last_{window}"),
                ("off_rating", f"off_rating_last_{window}"),
                ("def_rating", f"def_rating_last_{window}"),
                ("pace", f"pace_last_{window}"),
                ("efg_pct", f"efg_pct_last_{window}"),
                ("tov_pct", f"tov_pct_last_{window}"),
                ("orb_pct", f"orb_pct_last_{window}"),
                ("ft_rate", f"ft_rate_last_{window}"),
            ]:
                df[output] = (
                    df[source]
                    .shift(1)
                    .rolling(window=window, min_periods=1)
                    .mean()
                )

        prev_date = df["game_date"].shift(1)
        rest_days = (df["game_date"] - prev_date).dt.total_seconds() / 86400.0 - 1.0
        df["rest_days"] = rest_days.fillna(7.0).clip(lower=0.0)
        df["b2b"] = (df["rest_days"] <= 0.0).astype(int)
        df["strength_of_schedule"] = df["opponent_win_pct"].shift(1).rolling(window=10, min_periods=1).mean().fillna(0.5)

        keep_columns = [
            "game_id",
            "team",
            "home_win_pct",
            "net_rating_last_5",
            "net_rating_last_10",
            "off_rating_last_10",
            "def_rating_last_10",
            "pace_last_10",
            "efg_pct_last_10",
            "tov_pct_last_10",
            "orb_pct_last_10",
            "ft_rate_last_10",
            "rest_days",
            "b2b",
            "strength_of_schedule",
        ]
        return df[keep_columns]

    def _assemble_training_table(
        self,
        schedule: pd.DataFrame,
        pregame_features: pd.DataFrame,
    ) -> pd.DataFrame:
        home_features = pregame_features.rename(
            columns={
                "team": "home_team",
                "home_win_pct": "home_win_pct",
                "net_rating_last_5": "home_net_rating_last_5",
                "net_rating_last_10": "home_net_rating_last_10",
                "off_rating_last_10": "home_off_rating_last_10",
                "def_rating_last_10": "home_def_rating_last_10",
                "pace_last_10": "home_pace_last_10",
                "efg_pct_last_10": "home_efg_pct_last_10",
                "tov_pct_last_10": "home_tov_pct_last_10",
                "orb_pct_last_10": "home_orb_pct_last_10",
                "ft_rate_last_10": "home_ft_rate_last_10",
                "rest_days": "home_rest_days",
                "b2b": "home_b2b",
                "strength_of_schedule": "home_strength_of_schedule",
            }
        )
        away_features = pregame_features.rename(
            columns={
                "team": "away_team",
                "home_win_pct": "away_win_pct",
                "net_rating_last_5": "away_net_rating_last_5",
                "net_rating_last_10": "away_net_rating_last_10",
                "off_rating_last_10": "away_off_rating_last_10",
                "def_rating_last_10": "away_def_rating_last_10",
                "pace_last_10": "away_pace_last_10",
                "efg_pct_last_10": "away_efg_pct_last_10",
                "tov_pct_last_10": "away_tov_pct_last_10",
                "orb_pct_last_10": "away_orb_pct_last_10",
                "ft_rate_last_10": "away_ft_rate_last_10",
                "rest_days": "away_rest_days",
                "b2b": "away_b2b",
                "strength_of_schedule": "away_strength_of_schedule",
            }
        )

        df = schedule.merge(home_features, on=["game_id", "home_team"], how="left")
        df = df.merge(away_features, on=["game_id", "away_team"], how="left")
        return df

    def _finalize_training_table(self, df: pd.DataFrame) -> pd.DataFrame:
        defaults = {
            "home_win_pct": 0.5,
            "away_win_pct": 0.5,
            "home_net_rating_last_5": 0.0,
            "away_net_rating_last_5": 0.0,
            "home_net_rating_last_10": 0.0,
            "away_net_rating_last_10": 0.0,
            "home_off_rating_last_10": 110.0,
            "away_off_rating_last_10": 110.0,
            "home_def_rating_last_10": 110.0,
            "away_def_rating_last_10": 110.0,
            "home_pace_last_10": 100.0,
            "away_pace_last_10": 100.0,
            "home_efg_pct_last_10": 0.5,
            "away_efg_pct_last_10": 0.5,
            "home_tov_pct_last_10": 0.12,
            "away_tov_pct_last_10": 0.12,
            "home_orb_pct_last_10": 0.25,
            "away_orb_pct_last_10": 0.25,
            "home_ft_rate_last_10": 0.20,
            "away_ft_rate_last_10": 0.20,
            "home_rest_days": 7.0,
            "away_rest_days": 7.0,
            "home_b2b": 0,
            "away_b2b": 0,
            "home_strength_of_schedule": 0.5,
            "away_strength_of_schedule": 0.5,
        }
        for column, default in defaults.items():
            df[column] = df[column].fillna(default)

        df["diff_win_pct"] = df["home_win_pct"] - df["away_win_pct"]
        df["diff_net_rating_last_5"] = df["home_net_rating_last_5"] - df["away_net_rating_last_5"]
        df["diff_net_rating_last_10"] = df["home_net_rating_last_10"] - df["away_net_rating_last_10"]
        df["diff_off_rating_last_10"] = df["home_off_rating_last_10"] - df["away_off_rating_last_10"]
        df["diff_def_rating_last_10"] = df["home_def_rating_last_10"] - df["away_def_rating_last_10"]
        df["diff_pace_last_10"] = df["home_pace_last_10"] - df["away_pace_last_10"]
        df["diff_efg_pct_last_10"] = df["home_efg_pct_last_10"] - df["away_efg_pct_last_10"]
        df["diff_tov_pct_last_10"] = df["home_tov_pct_last_10"] - df["away_tov_pct_last_10"]
        df["diff_orb_pct_last_10"] = df["home_orb_pct_last_10"] - df["away_orb_pct_last_10"]
        df["diff_ft_rate_last_10"] = df["home_ft_rate_last_10"] - df["away_ft_rate_last_10"]
        df["diff_rest_days"] = df["home_rest_days"] - df["away_rest_days"]
        df["diff_strength_of_schedule"] = df["home_strength_of_schedule"] - df["away_strength_of_schedule"]

        return df[CORE_ID_COLUMNS + TARGET_COLUMNS + ALL_FEATURE_COLUMNS]

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
