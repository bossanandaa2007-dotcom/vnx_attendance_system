from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "matches.csv"
    outputs_dir = project_root / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path)

    # Clean columns
    df.columns = [c.strip() for c in df.columns]

    # Clean rows and keep only needed columns for analysis
    df_clean = df.dropna(subset=["winner"]).copy()
    keep_cols = ["season", "winner", "venue", "toss_decision"]
    df_clean = df_clean[keep_cols]

    # Normalize types
    df_clean["season"] = df_clean["season"].astype(str)
    df_clean["winner"] = df_clean["winner"].astype(str)
    df_clean["venue"] = df_clean["venue"].astype(str)
    df_clean["toss_decision"] = df_clean["toss_decision"].astype(str)

    # Analysis 1: Team with most wins
    team_wins = df_clean["winner"].value_counts()
    team_wins.to_csv(outputs_dir / "team_wins.csv", header=["wins"])

    # Analysis 2: Matches per season
    matches_per_season = df_clean.groupby("season").size().sort_index()
    matches_per_season.to_csv(outputs_dir / "matches_per_season.csv", header=["matches"])

    # Analysis 3: Top venues
    top_venues = df_clean["venue"].value_counts()
    top_venues.to_csv(outputs_dir / "top_venues.csv", header=["matches"])

    # Plot 1: Team wins bar chart
    plt.figure(figsize=(12, 6))
    team_wins.plot(kind="bar")
    plt.title("Team vs Total Wins")
    plt.xlabel("Team")
    plt.ylabel("Total Wins")
    plt.tight_layout()
    plt.savefig(outputs_dir / "team_wins_bar.png", dpi=150)
    plt.close()

    # Plot 2: Matches per season line chart
    plt.figure(figsize=(10, 5))
    matches_per_season.plot(kind="line", marker="o")
    plt.title("Matches per Season")
    plt.xlabel("Season")
    plt.ylabel("Number of Matches")
    plt.tight_layout()
    plt.savefig(outputs_dir / "matches_per_season_line.png", dpi=150)
    plt.close()

    # Plot 3: Toss decision vs win count scatter
    toss_counts = df_clean["toss_decision"].value_counts()
    x_labels = list(toss_counts.index)
    x_positions = list(range(len(x_labels)))
    y_values = toss_counts.values

    plt.figure(figsize=(8, 5))
    plt.scatter(x_positions, y_values)
    plt.title("Toss Decision vs Win Count")
    plt.xlabel("Toss Decision")
    plt.ylabel("Win Count")
    plt.xticks(x_positions, x_labels)
    plt.tight_layout()
    plt.savefig(outputs_dir / "toss_vs_win_scatter.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    main()
