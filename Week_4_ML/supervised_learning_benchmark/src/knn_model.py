"""KNN model builder and trainer."""

from __future__ import annotations

import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build_knn(k: int = 5) -> Pipeline:
    """Build a KNN pipeline with scaling.

    Args:
        k: Number of nearest neighbors.

    Returns:
        A fitted-ready sklearn Pipeline.
    """
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", KNeighborsClassifier(n_neighbors=k)),
        ]
    )


def train_knn(X_train: np.ndarray, y_train: np.ndarray, k: int = 5) -> Pipeline:
    """Train and return a KNN model."""
    model = build_knn(k=k)
    model.fit(X_train, y_train)
    return model
