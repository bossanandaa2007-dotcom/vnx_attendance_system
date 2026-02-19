# Data Files

This project uses IPL match data sourced from JSON files (Cricsheet format) and converted into a single CSV for analysis.

## Files

- `matches.csv` is generated from the JSON files under `_extracted/` using:

```bash
python scripts/convert_json_to_matches.py --input _extracted --output data/matches.csv
```

## Notes

- The JSON data remains in `_extracted/` if you want to regenerate the CSV or inspect raw match data.
- Only `matches.csv` is required for the Week 2 analysis workflow.
