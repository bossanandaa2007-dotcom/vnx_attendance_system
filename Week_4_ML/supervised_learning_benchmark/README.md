# Supervised Learning Benchmark (Week 4 Day 1 + Day 2)

This project compares `KNN`, `SVM (linear)`, `SVM (RBF)`, `Decision Tree`, and `Random Forest` on the Iris dataset using scikit-learn.

## Project Structure

```text
supervised_learning_benchmark/
src/
  data_loader.py
  knn_model.py
  svm_model.py
  decision_tree_model.py
  random_forest_model.py
  tune_random_forest.py
  evaluate.py
  main.py
notebooks/
  day2_gridsearch_comparison.ipynb
outputs/
requirements.txt
README.md
```

## Design Notes

- All models use the **same train/test split** from one call to `train_test_split(..., stratify=y)`.
- KNN and SVM models use `StandardScaler` inside sklearn pipelines.
- Decision Tree does not require scaling and is run without scaler by default (`use_scaler=False`) while still using a consistent pipeline interface.
- Random Forest also does not require scaling, but a scaler step is included in its pipeline for consistency across model builders.

## Setup (Windows PowerShell)

```powershell
cd Week_4_ML/supervised_learning_benchmark
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Day-1 Run Commands

```powershell
python src/main.py --model all --test-size 0.2 --random-state 42
python src/main.py --model knn
python src/main.py --model svm_linear
python src/main.py --model svm_rbf
python src/main.py --model decision_tree
```

## Day-2 Run Commands

```powershell
python src/main.py --model random_forest
python src/main.py --model rf_tuned
python src/main.py --model all
```

## GridSearchCV (Simple Explanation)

`GridSearchCV` tries many hyperparameter combinations, evaluates each combination with cross-validation on the training set, and picks the best one based on a scoring metric (here, `f1_macro`).

## CLI Arguments

- `--model`: `knn | svm_linear | svm_rbf | decision_tree | random_forest | rf_tuned | all`
- `--test-size`: float split ratio for test set (default: `0.2`)
- `--random-state`: random seed for reproducibility (default: `42`)

## Outputs

After each run, files are written to `outputs/`:

- `metrics_report.json`
- `metrics_report.txt`
- `confusion_matrix.png` (combined plot for selected models)
- `confusion_matrix_<model>.png` (per-model confusion matrix)

For tuned Random Forest (`--model rf_tuned`), these are also created:

- `best_params.json`
- `gridsearch_results.csv` (top 50 rows)
