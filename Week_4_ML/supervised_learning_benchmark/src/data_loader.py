#Data loading utilities for the supervised learning benchmark.

from __future__ import annotations

from typing import Tuple

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split


ArrayPair = Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]


def load_data(test_size: float = 0.2, random_state: int = 42) -> ArrayPair:
    """Load Iris data and return a stratified train/test split.

    Args:
        test_size: Fraction of data to reserve for testing.
        random_state: Seed used for deterministic splitting.

    Returns:
        Tuple of X_train, X_test, y_train, y_test, and class_names.
    """
    dataset = load_iris()
    X = np.asarray(dataset.data)
    y = np.asarray(dataset.target)
    class_names = np.asarray(dataset.target_names)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
    return X_train, X_test, y_train, y_test, class_names
