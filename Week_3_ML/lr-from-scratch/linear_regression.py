import numpy as np
#TRAINING DATA (Known relationship: y = 2x + 1)
x_train = np.array([1, 2, 3, 4, 5], dtype=float)
y_train = np.array([3, 5, 7, 9, 11], dtype=float)
#INITIalizing MODEL PARAMETERS
w = 0.0   # weight (slope)
b = 0.0   # bias (intercept)
#PREDICTION FUNCTION (MODEL)
def predict(x, w, b):
   #Linear Regression hypothesis function
    #y = wx + b
    return w * x + b
#COST FUNCTION (MEAN SQUARED ERROR)
def mean_squared_error(y_true, y_pred):
#Adding MSE
    return np.mean((y_true - y_pred) ** 2)
#TRAINING FUNCTION (GRADIENT DESCENT)
def train(x, y, w, b, learning_rate, epochs):
    n = len(x)
    for epoch in range(epochs):
        # Forward pass (predictions)
        y_pred = predict(x, w, b)
        # Gradients
        dw = (-2 / n) * np.sum(x * (y - y_pred))
        db = (-2 / n) * np.sum(y - y_pred)
        # Update parameters
        w = w - learning_rate * dw
        b = b - learning_rate * db
        # Cost calculation
        cost = mean_squared_error(y, y_pred)
        if epoch % 100 == 0:
            print(f"Epoch {epoch}: Cost = {cost:.4f}")
    return w, b
#TRAINing THE MODEL
learning_rate = 0.01
epochs = 1000
print("Training the model...\n")
w, b = train(x_train, y_train, w, b, learning_rate, epochs)
print("\nTraining completed!")
print("Final weight (w):", w)
print("Final bias (b):", b)
#PREDICT OUTPUT FOR NEW INPUTS (INFERENCE)
x_new = np.array([1, 2, 3, 4, 5], dtype=float)
predicted_output = predict(x_new, w, b)
print("\nNew Inputs:", x_new)
print("Predicted Outputs:", predicted_output)
