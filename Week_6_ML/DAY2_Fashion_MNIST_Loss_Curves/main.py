import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------
# 1. Class Names for Fashion MNIST
# ---------------------------------------------------------
class_names = [
    "T-shirt/top",
    "Trouser",
    "Pullover",
    "Dress",
    "Coat",
    "Sandal",
    "Shirt",
    "Sneaker",
    "Bag",
    "Ankle boot"
]


# ---------------------------------------------------------
# 2. Load Fashion MNIST Dataset
# ---------------------------------------------------------
# Fashion MNIST contains 28x28 grayscale images of clothing items.
# x_train = training images
# y_train = training labels
# x_test = testing images
# y_test = testing labels

(x_train, y_train), (x_test, y_test) = keras.datasets.fashion_mnist.load_data()

print("Training images shape:", x_train.shape)
print("Training labels shape:", y_train.shape)
print("Testing images shape:", x_test.shape)
print("Testing labels shape:", y_test.shape)


# ---------------------------------------------------------
# 3. Normalize Pixel Values
# ---------------------------------------------------------
# Original range: 0 to 255
# New range: 0 to 1

x_train = x_train / 255.0
x_test = x_test / 255.0


# ---------------------------------------------------------
# 4. Build Dense Neural Network Model
# ---------------------------------------------------------
# Input image: 28x28
# Flatten: 784 values
# Dense layers: learn clothing patterns
# Softmax: gives probability for 10 clothing classes

model = keras.Sequential([
    layers.Flatten(input_shape=(28, 28)),
    layers.Dense(256, activation="relu"),
    layers.Dense(128, activation="relu"),
    layers.Dense(10, activation="softmax")
])


# ---------------------------------------------------------
# 5. Compile Model
# ---------------------------------------------------------
# Adam optimizer updates weights.
# Sparse categorical crossentropy is used because labels are integers.
# Accuracy shows correct prediction percentage.

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


# ---------------------------------------------------------
# 6. Save Model Summary
# ---------------------------------------------------------

with open("Week_6_ML/DAY2_Fashion_MNIST_Loss_Curves/model_summary.txt", "w", encoding="utf-8") as file:
    model.summary(print_fn=lambda line: file.write(line + "\n"))

model.summary()


# ---------------------------------------------------------
# 7. Train Model and Store History
# ---------------------------------------------------------
# epochs=10 means the model sees the full training data 10 times.
# validation_split=0.2 means 20% of training data is used for validation.

history = model.fit(
    x_train,
    y_train,
    epochs=10,
    validation_split=0.2,
    batch_size=64
)


# ---------------------------------------------------------
# 8. Evaluate Model on Test Data
# ---------------------------------------------------------

test_loss, test_accuracy = model.evaluate(x_test, y_test)

print("\nFinal Test Loss:", test_loss)
print("Final Test Accuracy:", test_accuracy)


# ---------------------------------------------------------
# 9. Plot Accuracy Curve
# ---------------------------------------------------------

plt.figure()
plt.plot(history.history["accuracy"], label="Training Accuracy")
plt.plot(history.history["val_accuracy"], label="Validation Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.title("Training Accuracy vs Validation Accuracy")
plt.legend()
plt.grid(True)
plt.savefig("Week_6_ML/DAY2_Fashion_MNIST_Loss_Curves/accuracy_curve.png")
plt.show()


# ---------------------------------------------------------
# 10. Plot Loss Curve
# ---------------------------------------------------------

plt.figure()
plt.plot(history.history["loss"], label="Training Loss")
plt.plot(history.history["val_loss"], label="Validation Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("Training Loss vs Validation Loss")
plt.legend()
plt.grid(True)
plt.savefig("Week_6_ML/DAY2_Fashion_MNIST_Loss_Curves/loss_curve.png")
plt.show()


# ---------------------------------------------------------
# 11. Make Predictions on First 10 Test Images
# ---------------------------------------------------------

predictions = model.predict(x_test[:10])

print("\nSample Predictions:")

for i in range(10):
    predicted_class = class_names[np.argmax(predictions[i])]
    actual_class = class_names[y_test[i]]

    print(f"Image {i + 1}: Predicted = {predicted_class}, Actual = {actual_class}")


# ---------------------------------------------------------
# 12. Print Final Learning Analysis
# ---------------------------------------------------------

final_train_accuracy = history.history["accuracy"][-1]
final_val_accuracy = history.history["val_accuracy"][-1]
final_train_loss = history.history["loss"][-1]
final_val_loss = history.history["val_loss"][-1]

print("\nTraining Analysis:")
print("Final Training Accuracy:", final_train_accuracy)
print("Final Validation Accuracy:", final_val_accuracy)
print("Final Training Loss:", final_train_loss)
print("Final Validation Loss:", final_val_loss)

gap = final_train_accuracy - final_val_accuracy

print("\nGeneralization Gap:", gap)

if gap > 0.08:
    print("Observation: Model may be overfitting.")
elif final_train_accuracy < 0.80 and final_val_accuracy < 0.80:
    print("Observation: Model may be underfitting.")
else:
    print("Observation: Model is learning reasonably well.")