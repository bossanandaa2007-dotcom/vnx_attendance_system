"""Evaluation utilities for supervised learning models."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def evaluate_model(
    name: str,
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> Tuple[Dict[str, Any], np.ndarray]:
    """Evaluate a model and return metrics plus confusion matrix."""
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    result: Dict[str, Any] = {
        "model": name,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision_macro": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
        "confusion_matrix": cm.tolist(),
    }
    return result, cm


def save_confusion_matrix_plot(
    cm: np.ndarray,
    labels: np.ndarray,
    output_dir: Path,
    model_name: str,
) -> Tuple[Path, Path]:
    """Save confusion matrix plot as model-specific and backward-compatible filenames."""
    output_dir.mkdir(parents=True, exist_ok=True)
    labels_list = [str(label) for label in labels]

    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.set_title(f"Confusion Matrix - {model_name}")
    ax.set_xticks(np.arange(len(labels_list)))
    ax.set_yticks(np.arange(len(labels_list)))
    ax.set_xticklabels(labels_list, rotation=45, ha="right")
    ax.set_yticklabels(labels_list)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")

    threshold = cm.max() / 2.0 if cm.size else 0.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            color = "white" if cm[i, j] > threshold else "black"
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color=color)

    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()

    model_png_path = output_dir / f"confusion_matrix_{model_name}.png"
    legacy_png_path = output_dir / "confusion_matrix.png"
    fig.savefig(model_png_path, dpi=150)
    fig.savefig(legacy_png_path, dpi=150)
    plt.close(fig)
    return model_png_path, legacy_png_path
