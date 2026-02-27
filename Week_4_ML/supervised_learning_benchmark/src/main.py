"""CLI runner for supervised learning benchmark on Iris."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from data_loader import load_data
from decision_tree_model import build_tree
from evaluate import evaluate_model, save_confusion_matrix_plot
from knn_model import build_knn
from random_forest_model import build_random_forest
from svm_model import build_svm_linear, build_svm_rbf
from tune_random_forest import tune_random_forest

MODEL_CHOICES = [
    "knn",
    "svm_linear",
    "svm_rbf",
    "decision_tree",
    "random_forest",
    "rf_tuned",
    "all",
]


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Supervised learning benchmark on Iris dataset.")
    parser.add_argument("--model", choices=MODEL_CHOICES, default="all", help="Model to run.")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test split size (0-1).")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed.")
    return parser.parse_args()


def get_models(selection: str, random_state: int) -> Dict[str, Pipeline]:
    """Build selected model(s) with a consistent interface."""
    registry: Dict[str, Pipeline] = {
        "knn": build_knn(k=5),
        "svm_linear": build_svm_linear(C=1.0),
        "svm_rbf": build_svm_rbf(C=1.0, gamma="scale"),
        "decision_tree": build_tree(max_depth=3, random_state=random_state, use_scaler=False),
        "random_forest": build_random_forest(random_state=random_state),
    }
    if selection == "all":
        return registry
    return {selection: registry[selection]}


def save_reports(
    output_dir: Path,
    results: List[Dict[str, Any]],
    model_selection: str,
    test_size: float,
    random_state: int,
) -> Tuple[Path, Path]:
    """Save JSON and text reports to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    payload: Dict[str, Any] = {
        "config": {
            "model": model_selection,
            "test_size": test_size,
            "random_state": random_state,
        },
        "results": results,
    }

    json_path = output_dir / "metrics_report.json"
    txt_path = output_dir / "metrics_report.txt"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines: List[str] = [
        "Supervised Learning Benchmark - Iris",
        "=" * 40,
        f"model={model_selection}",
        f"test_size={test_size}",
        f"random_state={random_state}",
        "",
    ]
    for item in results:
        lines.append(f"Model: {item['model']}")
        lines.append(f"  Accuracy: {item['accuracy']:.4f}")
        lines.append(f"  Precision (macro): {item['precision_macro']:.4f}")
        lines.append(f"  Recall (macro): {item['recall_macro']:.4f}")
        lines.append(f"  F1 (macro): {item['f1_macro']:.4f}")
        lines.append(f"  Confusion Matrix: {item['confusion_matrix']}")
        lines.append("")

    txt_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return json_path, txt_path


def save_tuning_artifacts(
    output_dir: Path,
    best_params: Dict[str, Any],
    cv_results_df: pd.DataFrame,
) -> Tuple[Path, Path]:
    """Save GridSearchCV outputs to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    best_params_path = output_dir / "best_params.json"
    grid_results_path = output_dir / "gridsearch_results.csv"

    best_params_path.write_text(json.dumps(best_params, indent=2), encoding="utf-8")
    cv_results_df.head(50).to_csv(grid_results_path, index=False)
    return best_params_path, grid_results_path


def save_combined_confusion_matrix(
    output_dir: Path,
    matrices: List[np.ndarray],
    labels: List[str],
    model_names: List[str],
) -> Path:
    """Save a combined confusion matrix image for all evaluated models."""
    cols = 2
    rows = int(np.ceil(len(matrices) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(10, 4 * rows))
    axes_arr = np.array(axes).reshape(-1)

    for idx, (cm, name) in enumerate(zip(matrices, model_names)):
        ax = axes_arr[idx]
        image = ax.imshow(cm, interpolation="nearest", cmap="Blues")
        ax.set_title(name)
        ax.set_xticks(np.arange(len(labels)))
        ax.set_yticks(np.arange(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_yticklabels(labels)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")

        threshold = cm.max() / 2.0 if cm.size else 0.0
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                color = "white" if cm[i, j] > threshold else "black"
                ax.text(j, i, str(cm[i, j]), ha="center", va="center", color=color)

        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    for idx in range(len(matrices), len(axes_arr)):
        axes_arr[idx].axis("off")

    fig.tight_layout()
    png_path = output_dir / "confusion_matrix.png"
    fig.savefig(png_path, dpi=150)
    plt.close(fig)
    return png_path


def main() -> None:
    """Run benchmark and save reports."""
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / "outputs"

    X_train, X_test, y_train, y_test, class_names = load_data(
        test_size=args.test_size,
        random_state=args.random_state,
    )

    results: List[Dict[str, Any]] = []
    confusion_matrices: List[np.ndarray] = []
    names: List[str] = []
    model_specific_paths: List[Path] = []

    if args.model == "rf_tuned":
        best_estimator, best_params, cv_results_df = tune_random_forest(
            X_train=X_train,
            y_train=y_train,
            random_state=args.random_state,
        )
        best_params_path, grid_results_path = save_tuning_artifacts(
            output_dir=output_dir,
            best_params=best_params,
            cv_results_df=cv_results_df,
        )

        metrics, cm = evaluate_model(name="rf_tuned", model=best_estimator, X_test=X_test, y_test=y_test)
        results.append(metrics)
        confusion_matrices.append(cm)
        names.append("rf_tuned")

        model_png_path, _ = save_confusion_matrix_plot(
            cm=cm,
            labels=class_names,
            output_dir=output_dir,
            model_name="rf_tuned",
        )
        model_specific_paths.append(model_png_path)

        print("Best params (rf_tuned):")
        print(json.dumps(best_params, indent=2))
        print(f"Saved best params: {best_params_path}")
        print(f"Saved grid search results: {grid_results_path}")
    else:
        models = get_models(selection=args.model, random_state=args.random_state)
        for name, model in models.items():
            model.fit(X_train, y_train)
            metrics, cm = evaluate_model(name=name, model=model, X_test=X_test, y_test=y_test)
            results.append(metrics)
            confusion_matrices.append(cm)
            names.append(name)

            model_png_path, _ = save_confusion_matrix_plot(
                cm=cm,
                labels=class_names,
                output_dir=output_dir,
                model_name=name,
            )
            model_specific_paths.append(model_png_path)

    json_path, txt_path = save_reports(
        output_dir=output_dir,
        results=results,
        model_selection=args.model,
        test_size=args.test_size,
        random_state=args.random_state,
    )
    png_path = save_combined_confusion_matrix(
        output_dir=output_dir,
        matrices=confusion_matrices,
        labels=[str(label) for label in class_names],
        model_names=names,
    )

    print("Run complete")
    print(f"Saved JSON report: {json_path}")
    print(f"Saved TXT report: {txt_path}")
    print(f"Saved confusion matrix image: {png_path}")
    for path in model_specific_paths:
        print(f"Saved per-model confusion matrix image: {path}")


if __name__ == "__main__":
    main()
