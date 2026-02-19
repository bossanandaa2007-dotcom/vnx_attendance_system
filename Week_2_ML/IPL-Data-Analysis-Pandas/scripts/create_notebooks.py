import json
from pathlib import Path


def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": text.splitlines(True)}


def write_notebook(path: Path, nb):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(nb, indent=2), encoding="utf-8")


root = Path(__file__).resolve().parents[1]
nb_dir = root / "notebooks"

# 01_data_overview.ipynb
cells = [
    md("# 01 Data Overview\n\nLoad the raw data and inspect its structure."),
    code(
        "import pandas as pd\n\n"
        "df = pd.read_csv('../data/matches.csv')\n"
        "df.head()"
    ),
    code(
        "df.info()"
    ),
]
write_notebook(nb_dir / "01_data_overview.ipynb", make_notebook(cells))

# 02_data_cleaning.ipynb
cells = [
    md("# 02 Data Cleaning\n\nClean only the columns required for analysis."),
    code(
        "import pandas as pd\n\n"
        "df = pd.read_csv('../data/matches.csv')\n"
        "df.columns = [c.strip() for c in df.columns]\n\n"
        "before_rows = len(df)\n"
        "df_clean = df.dropna(subset=['winner']).copy()\n"
        "after_rows = len(df_clean)\n\n"
        "keep_cols = ['season', 'winner', 'venue', 'toss_decision']\n"
        "df_clean = df_clean[keep_cols]\n\n"
        "print('Total rows before cleaning:', before_rows)\n"
        "print('Total rows after cleaning:', after_rows)\n"
        "print('Missing values:', df_clean.isna().sum().sum())\n\n"
        "df_clean.head()"
    ),
]
write_notebook(nb_dir / "02_data_cleaning.ipynb", make_notebook(cells))

# 03_eda_analysis.ipynb
cells = [
    md("# 03 EDA Analysis\n\nSimple tables for team wins, matches per season, and top venues."),
    code(
        "import pandas as pd\n\n"
        "df = pd.read_csv('../data/matches.csv')\n"
        "df.columns = [c.strip() for c in df.columns]\n"
        "df = df.dropna(subset=['winner']).copy()\n"
        "df = df[['season', 'winner', 'venue', 'toss_decision']]\n\n"
        "team_wins = df['winner'].value_counts()\n"
        "matches_per_season = df.groupby('season').size().sort_index()\n"
        "top_venues = df['venue'].value_counts()\n\n"
        "team_wins.head(10)"
    ),
    code("matches_per_season.head(10)"),
    code("top_venues.head(10)"),
]
write_notebook(nb_dir / "03_eda_analysis.ipynb", make_notebook(cells))

# 04_visualizations.ipynb
cells = [
    md("# 04 Visualizations\n\nGenerate the required plots and save them in outputs/."),
    code(
        "import pandas as pd\n"
        "import matplotlib.pyplot as plt\n"
        "from pathlib import Path\n\n"
        "out_dir = Path('../outputs')\n"
        "out_dir.mkdir(parents=True, exist_ok=True)\n\n"
        "df = pd.read_csv('../data/matches.csv')\n"
        "df.columns = [c.strip() for c in df.columns]\n"
        "df = df.dropna(subset=['winner']).copy()\n"
        "df = df[['season', 'winner', 'venue', 'toss_decision']]\n\n"
        "team_wins = df['winner'].value_counts()\n"
        "matches_per_season = df.groupby('season').size().sort_index()\n"
        "toss_counts = df['toss_decision'].value_counts()\n\n"
        "plt.figure(figsize=(12, 6))\n"
        "team_wins.plot(kind='bar')\n"
        "plt.title('Team vs Total Wins')\n"
        "plt.xlabel('Team')\n"
        "plt.ylabel('Total Wins')\n"
        "plt.tight_layout()\n"
        "plt.savefig(out_dir / 'team_wins_bar.png', dpi=150)\n"
        "plt.close()\n\n"
        "plt.figure(figsize=(10, 5))\n"
        "matches_per_season.plot(kind='line', marker='o')\n"
        "plt.title('Matches per Season')\n"
        "plt.xlabel('Season')\n"
        "plt.ylabel('Number of Matches')\n"
        "plt.tight_layout()\n"
        "plt.savefig(out_dir / 'matches_per_season_line.png', dpi=150)\n"
        "plt.close()\n\n"
        "x_labels = list(toss_counts.index)\n"
        "x_positions = list(range(len(x_labels)))\n"
        "y_values = toss_counts.values\n\n"
        "plt.figure(figsize=(8, 5))\n"
        "plt.scatter(x_positions, y_values)\n"
        "plt.title('Toss Decision vs Win Count')\n"
        "plt.xlabel('Toss Decision')\n"
        "plt.ylabel('Win Count')\n"
        "plt.xticks(x_positions, x_labels)\n"
        "plt.tight_layout()\n"
        "plt.savefig(out_dir / 'toss_vs_win_scatter.png', dpi=150)\n"
        "plt.close()"
    ),
]
write_notebook(nb_dir / "04_visualizations.ipynb", make_notebook(cells))
