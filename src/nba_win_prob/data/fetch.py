import argparse
import json
from pathlib import Path

import requests

from src.nba_win_prob.config import NBA_HEADERS, RAW_DIR

LEAGUEGAMEFINDER_URL = "https://stats.nba.com/stats/leaguegamefinder"


def fetch_games(season: str) -> list[dict]:
    params = {
        "College": "",
        "Conference": "",
        "Country": "",
        "DateFrom": "",
        "DateTo": "",
        "Division": "",
        "DraftNumber": "",
        "DraftRound": "",
        "DraftTeamID": "",
        "DraftYear": "",
        "EqAST": "",
        "EqBLK": "",
        "EqDD": "",
        "EqDREB": "",
        "EqFG3A": "",
        "EqFG3M": "",
        "EqFG3_PCT": "",
        "EqFGA": "",
        "EqFGM": "",
        "EqFG_PCT": "",
        "EqFTA": "",
        "EqFTM": "",
        "EqFT_PCT": "",
        "EqMINUTES": "",
        "EqOREB": "",
        "EqPF": "",
        "EqPTS": "",
        "EqREB": "",
        "EqSTL": "",
        "EqTD": "",
        "EqTOV": "",
        "GameID": "",
        "GtAST": "",
        "GtBLK": "",
        "GtDD": "",
        "GtDREB": "",
        "GtFG3A": "",
        "GtFG3M": "",
        "GtFG3_PCT": "",
        "GtFGA": "",
        "GtFGM": "",
        "GtFG_PCT": "",
        "GtFTA": "",
        "GtFTM": "",
        "GtFT_PCT": "",
        "GtMINUTES": "",
        "GtOREB": "",
        "GtPF": "",
        "GtPTS": "",
        "GtREB": "",
        "GtSTL": "",
        "GtTD": "",
        "GtTOV": "",
        "LeagueID": "00",
        "Location": "",
        "LtAST": "",
        "LtBLK": "",
        "LtDD": "",
        "LtDREB": "",
        "LtFG3A": "",
        "LtFG3M": "",
        "LtFG3_PCT": "",
        "LtFGA": "",
        "LtFGM": "",
        "LtFG_PCT": "",
        "LtFTA": "",
        "LtFTM": "",
        "LtFT_PCT": "",
        "LtMINUTES": "",
        "LtOREB": "",
        "LtPF": "",
        "LtPTS": "",
        "LtREB": "",
        "LtSTL": "",
        "LtTD": "",
        "LtTOV": "",
        "Outcome": "",
        "PORound": "",
        "PlayerID": "",
        "PlayerOrTeam": "T",
        "Season": season,
        "SeasonSegment": "",
        "SeasonType": "Regular Season",
        "StarterBench": "",
        "TeamID": "",
        "VsConference": "",
        "VsDivision": "",
        "VsTeamID": "",
    }
    response = requests.get(LEAGUEGAMEFINDER_URL, params=params, headers=NBA_HEADERS, timeout=30)
    response.raise_for_status()
    payload = response.json()
    result_set = payload["resultSets"][0]
    headers = result_set["headers"]
    return [dict(zip(headers, row)) for row in result_set["rowSet"]]


def save_games(season: str, rows: list[dict]) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / f"games_{season}.json"
    out_path.write_text(json.dumps(rows, indent=2))
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", required=True)
    args = parser.parse_args()

    rows = fetch_games(args.season)
    out_path = save_games(args.season, rows)
    print(f"saved {len(rows)} team-game rows to {out_path}")


if __name__ == "__main__":
    main()
