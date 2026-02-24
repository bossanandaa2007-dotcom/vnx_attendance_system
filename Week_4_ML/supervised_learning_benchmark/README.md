# Supervised Learning Benchmark (Week 4 Day 1)

This project compares `KNN`, `SVM (linear)`, `SVM (RBF)`, and `Decision Tree` on the Iris dataset using scikit-learn.

## Project Structure

```text
supervised_learning_benchmark/
src/
  data_loader.py
  knn_model.py
  svm_model.py
  decision_tree_model.py
  evaluate.py
  main.py
outputs/
requirements.txt
README.md
```

## Design Notes

- All models use the **same train/test split** from one call to `train_test_split(..., stratify=y)`.
- KNN and SVM models use `StandardScaler` inside sklearn pipelines.
- Decision Tree does not require scaling and is run without scaler by default (`use_scaler=False`) while still using a consistent pipeline interface.

## Setup (Windows PowerShell)

```powershell
cd Week_4_ML/supervised_learning_benchmark
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run Commands

```powershell
python src/main.py --model all --test-size 0.2 --random-state 42
python src/main.py --model knn
python src/main.py --model svm_linear
python src/main.py --model svm_rbf
python src/main.py --model decision_tree
```

## CLI Arguments

- `--model`: `knn | svm_linear | svm_rbf | decision_tree | all`
- `--test-size`: float split ratio for test set (default: `0.2`)
- `--random-state`: random seed for reproducibility (default: `42`)

## Outputs

After each run, files are written to `outputs/`:

- `metrics_report.json`
- `metrics_report.txt`
- `confusion_matrix.png` (combined plot for selected models)
