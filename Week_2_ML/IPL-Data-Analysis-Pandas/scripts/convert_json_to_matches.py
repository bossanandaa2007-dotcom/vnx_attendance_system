import argparse
import csv
import json
from pathlib import Path

def safe_first(value, default=None):
    if isinstance(value, list) and value:
        return value[0]
    return default


def normalize_season(info, match_date):
    season = info.get("season")
    if season is not None:
        return season
    if match_date and len(match_date) >= 4:
        try:
            return int(match_date[:4])
        except ValueError:
            return match_date[:4]
    return ""


def extract_match_row(match_path: Path) -> dict:
    with match_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    info = data.get("info", {})
    match_id = match_path.stem

    teams = info.get("teams", [])
    team1 = teams[0] if len(teams) > 0 else ""
    team2 = teams[1] if len(teams) > 1 else ""

    dates = info.get("dates", [])
    match_date = safe_first(dates, "")

    toss = info.get("toss", {})
    outcome = info.get("outcome", {})

    row = {
        "match_id": match_id,
        "season": normalize_season(info, match_date),
        "date": match_date,
        "team1": team1,
        "team2": team2,
        "winner": outcome.get("winner", ""),
        "venue": info.get("venue", ""),
        "city": info.get("city", ""),
        "toss_winner": toss.get("winner", ""),
        "toss_decision": toss.get("decision", ""),
        "result": outcome.get("result", ""),
        "player_of_match": safe_first(info.get("player_of_match", []), ""),
    }

    return row


def build_matches_csv(input_dir: Path, output_csv: Path) -> int:
    json_files = sorted(input_dir.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {input_dir}")

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "match_id",
        "season",
        "date",
        "team1",
        "team2",
        "winner",
        "venue",
        "city",
        "toss_winner",
        "toss_decision",
        "result",
        "player_of_match",
    ]

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for match_path in json_files:
            writer.writerow(extract_match_row(match_path))

    return len(json_files)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert IPL JSON files to matches.csv")
    parser.add_argument("--input", default="_extracted", help="Folder with JSON files")
    parser.add_argument("--output", default="data/matches.csv", help="Output CSV path")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_csv = Path(args.output)

    count = build_matches_csv(input_dir, output_csv)
    print(f"Wrote {count} matches to {output_csv}")


if __name__ == "__main__":
    main()
