"""SVM model builders and trainer."""

from __future__ import annotations

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def build_svm_linear(C: float = 1.0) -> Pipeline:
    """Build a linear-kernel SVM pipeline with scaling."""
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", SVC(kernel="linear", C=C)),
        ]
    )


def build_svm_rbf(C: float = 1.0, gamma: str = "scale") -> Pipeline:
    """Build an RBF-kernel SVM pipeline with scaling."""
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", SVC(kernel="rbf", C=C, gamma=gamma)),
        ]
    )


def train_svm(
    X_train: np.ndarray,
    y_train: np.ndarray,
    variant: str = "linear",
    C: float = 1.0,
    gamma: str = "scale",
) -> Pipeline:
    """Train and return an SVM model for the selected variant."""
    if variant == "linear":
        model = build_svm_linear(C=C)
    elif variant == "rbf":
        model = build_svm_rbf(C=C, gamma=gamma)
    else:
        raise ValueError("variant must be 'linear' or 'rbf'")

    model.fit(X_train, y_train)
    return model
