"""Random Forest model builder."""

from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build_random_forest(random_state: int) -> Pipeline:
    """Build a Random Forest pipeline with a scaler for API consistency."""
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "rf",
                RandomForestClassifier(
                    n_estimators=200,
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ]
    )
