"""Decision Tree model builder and trainer."""

from __future__ import annotations

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


def build_tree(max_depth: int = 3, random_state: int = 42, use_scaler: bool = False) -> Pipeline:
    """Build a Decision Tree pipeline.

    Decision trees do not require feature scaling, so `use_scaler` defaults to False.
    """
    steps = []
    if use_scaler:
        steps.append(("scaler", StandardScaler()))
    steps.append(
        (
            "classifier",
            DecisionTreeClassifier(max_depth=max_depth, random_state=random_state),
        )
    )
    return Pipeline(steps=steps)


def train_tree(
    X_train: np.ndarray,
    y_train: np.ndarray,
    max_depth: int = 3,
    random_state: int = 42,
    use_scaler: bool = False,
) -> Pipeline:
    """Train and return a Decision Tree model."""
    model = build_tree(max_depth=max_depth, random_state=random_state, use_scaler=use_scaler)
    model.fit(X_train, y_train)
    return model
