# IPL Match Data Analysis (Pandas + Matplotlib)

This project converts IPL JSON match files into a clean `matches.csv`, then performs basic EDA and visualizations.

## Structure

```
IPL-Data-Analysis-Pandas/
├── data/
│   └── matches.csv
├── outputs/
│   ├── team_wins_bar.png
│   ├── matches_per_season_line.png
│   └── toss_vs_win_scatter.png
├── notebooks/
├── scripts/
│   ├── convert_json_to_matches.py
│   └── run_analysis.py
└── requirements.txt
```

## Quick Start

1. Convert JSON to CSV:

```bash
python scripts/convert_json_to_matches.py --input _extracted --output data/matches.csv
```

2. Run analysis and generate plots:

```bash
python scripts/run_analysis.py
```

Outputs are saved in `outputs/`.
