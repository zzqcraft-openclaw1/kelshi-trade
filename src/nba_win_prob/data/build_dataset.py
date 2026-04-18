import argparse
import json
from collections import defaultdict, deque
from dataclasses import dataclass

import pandas as pd

from src.nba_win_prob.config import DEFAULT_LAST_N, DEFAULT_MIN_GAMES, PROCESSED_DIR, RAW_DIR

STAT_COLS = [
    "PTS",
    "REB",
    "AST",
    "TOV",
    "STL",
    "BLK",
    "FG_PCT",
    "FG3_PCT",
    "FT_PCT",
    "PLUS_MINUS",
]


@dataclass
class TeamState:
    games: deque
    last_game_date: pd.Timestamp | None = None


def parse_matchup(matchup: str) -> tuple[bool, str]:
    if " vs. " in matchup:
        team, opp = matchup.split(" vs. ")
        return True, opp.strip()
    team, opp = matchup.split(" @ ")
    return False, opp.strip()


def load_raw_games(season: str) -> pd.DataFrame:
    path = RAW_DIR / f"games_{season}.json"
    rows = json.loads(path.read_text())
    df = pd.DataFrame(rows)
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    df["WL_BIN"] = (df["WL"] == "W").astype(int)
    return df.sort_values(["GAME_DATE", "GAME_ID", "TEAM_ID"]).reset_index(drop=True)


def rolling_means(history: deque, cols: list[str]) -> dict[str, float]:
    if not history:
        return {f"roll_{col.lower()}": float("nan") for col in cols}
    hist_df = pd.DataFrame(list(history))
    return {f"roll_{col.lower()}": hist_df[col].mean() for col in cols}


def build_examples(df: pd.DataFrame, last_n: int, min_games: int) -> pd.DataFrame:
    team_histories: dict[int, TeamState] = defaultdict(lambda: TeamState(games=deque(maxlen=last_n)))
    records: list[dict] = []

    for game_id, game_rows in df.groupby("GAME_ID", sort=True):
        if len(game_rows) != 2:
            continue

        game_rows = game_rows.sort_values("TEAM_ID")
        team_rows = []
        for _, row in game_rows.iterrows():
            is_home, opp_abbr = parse_matchup(row["MATCHUP"])
            state = team_histories[row["TEAM_ID"]]
            team_rows.append(
                {
                    "row": row,
                    "is_home": is_home,
                    "opp_abbr": opp_abbr,
                    "state": state,
                    "rolling": rolling_means(state.games, STAT_COLS),
                    "games_seen": len(state.games),
                    "rest_days": (
                        (row["GAME_DATE"] - state.last_game_date).days - 1 if state.last_game_date is not None else None
                    ),
                }
            )

        home = next((x for x in team_rows if x["is_home"]), None)
        away = next((x for x in team_rows if not x["is_home"]), None)
        if home is None or away is None:
            continue

        if home["games_seen"] >= min_games and away["games_seen"] >= min_games:
            record = {
                "game_id": game_id,
                "game_date": home["row"]["GAME_DATE"],
                "season_id": home["row"]["SEASON_ID"],
                "home_team_id": home["row"]["TEAM_ID"],
                "away_team_id": away["row"]["TEAM_ID"],
                "home_team": home["row"]["TEAM_ABBREVIATION"],
                "away_team": away["row"]["TEAM_ABBREVIATION"],
                "home_win": home["row"]["WL_BIN"],
                "home_rest_days": home["rest_days"],
                "away_rest_days": away["rest_days"],
                "home_b2b": int((home["rest_days"] or 99) <= 0),
                "away_b2b": int((away["rest_days"] or 99) <= 0),
            }
            for col in STAT_COLS:
                home_val = home["rolling"][f"roll_{col.lower()}"]
                away_val = away["rolling"][f"roll_{col.lower()}"]
                record[f"home_{col.lower()}"] = home_val
                record[f"away_{col.lower()}"] = away_val
                record[f"delta_{col.lower()}"] = home_val - away_val
            records.append(record)

        for item in team_rows:
            row = item["row"]
            snapshot = {col: row[col] for col in STAT_COLS}
            item["state"].games.append(snapshot)
            item["state"].last_game_date = row["GAME_DATE"]

    return pd.DataFrame(records).sort_values("game_date").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", required=True)
    parser.add_argument("--last-n", type=int, default=DEFAULT_LAST_N)
    parser.add_argument("--min-games", type=int, default=DEFAULT_MIN_GAMES)
    args = parser.parse_args()

    df = load_raw_games(args.season)
    dataset = build_examples(df, last_n=args.last_n, min_games=args.min_games)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / f"pregame_dataset_{args.season}.parquet"
    dataset.to_parquet(out_path, index=False)
    print(f"saved {len(dataset)} examples to {out_path}")


if __name__ == "__main__":
    main()
