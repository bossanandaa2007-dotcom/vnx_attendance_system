"""Random Forest hyperparameter tuning utilities."""

from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

from random_forest_model import build_random_forest


def tune_random_forest(
    X_train: np.ndarray,
    y_train: np.ndarray,
    random_state: int,
) -> Tuple[Pipeline, Dict[str, Any], pd.DataFrame]:
    """Tune Random Forest with GridSearchCV and return best artifacts."""
    model = build_random_forest(random_state=random_state)
    param_grid = {
        "rf__n_estimators": [100, 200, 400],
        "rf__max_depth": [None, 3, 5, 10],
        "rf__min_samples_split": [2, 5, 10],
        "rf__max_features": ["sqrt", "log2", None],
    }

    search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=5,
        scoring="f1_macro",
        n_jobs=-1,
    )
    search.fit(X_train, y_train)

    cv_results_df = pd.DataFrame(search.cv_results_).sort_values(
        by="mean_test_score",
        ascending=False,
    )
    best_estimator = search.best_estimator_
    best_params: Dict[str, Any] = search.best_params_
    return best_estimator, best_params, cv_results_df
