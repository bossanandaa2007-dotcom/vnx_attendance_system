import numpy as np
# 1) Core math helpers
def sigmoid(z: np.ndarray) -> np.ndarray:
    # Numerical stability: clip z to avoid overflow in exp
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))


def binary_cross_entropy(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    # Avoid log(0)
    eps = 1e-15
    y_prob = np.clip(y_prob, eps, 1 - eps)
    return float(-np.mean(y_true * np.log(y_prob) + (1 - y_true) * np.log(1 - y_prob)))


# 2) Logistic Regression (from scratch)
class LogisticRegressionScratch:
    def __init__(self, learning_rate: float = 0.1, epochs: int = 1000):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.w = None  # shape: (n_features,)
        self.b = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray, verbose_every: int = 100):
        """
        X: (n_samples, n_features)
        y: (n_samples,) with labels {0,1}
        """
        n_samples, n_features = X.shape
        self.w = np.zeros(n_features, dtype=float)
        self.b = 0.0

        for epoch in range(self.epochs):
            # Forward pass
            z = X @ self.w + self.b
            y_prob = sigmoid(z)

            # Gradients (derivative of BCE w.r.t w,b)
            dw = (1 / n_samples) * (X.T @ (y_prob - y))
            db = float((1 / n_samples) * np.sum(y_prob - y))

            # Update
            self.w -= self.learning_rate * dw
            self.b -= self.learning_rate * db

            # Logging
            if verbose_every and epoch % verbose_every == 0:
                loss = binary_cross_entropy(y, y_prob)
                print(f"Epoch {epoch}: Loss = {loss:.4f}")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        z = X @ self.w + self.b
        return sigmoid(z)

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(X) >= threshold).astype(int)

# 3) Small dataset demo (AND gate)
if __name__ == "__main__":
    # AND gate dataset
    # X1 X2 -> y
    X = np.array([
        [0, 0],
        [0, 1],
        [1, 0],
        [1, 1],
    ], dtype=float)

    y = np.array([0, 0, 0, 1], dtype=float)

    model = LogisticRegressionScratch(learning_rate=0.5, epochs=2000)
    print("Training Logistic Regression from scratch...\n")
    model.fit(X, y, verbose_every=200)

    print("\nLearned parameters:")
    print("w =", model.w)
    print("b =", model.b)

    probs = model.predict_proba(X)
    preds = model.predict(X)

    print("\nPredicted probabilities:", np.round(probs, 4))
    print("Predicted classes:", preds.astype(int))
    print("True classes:", y.astype(int))

    accuracy = np.mean(preds == y)
    print("\nAccuracy:", round(float(accuracy), 4))
