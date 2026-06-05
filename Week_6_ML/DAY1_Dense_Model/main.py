import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Load MNIST dataset
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

print("Training images shape:", x_train.shape)
print("Training labels shape:", y_train.shape)
print("Testing images shape:", x_test.shape)
print("Testing labels shape:", y_test.shape)

# Normalize pixel values from 0-255 to 0-1
x_train = x_train / 255.0
x_test = x_test / 255.0

# Build Dense Neural Network
model = keras.Sequential([
    keras.Input(shape=(28, 28)),
    layers.Flatten(),
    layers.Dense(128, activation="relu"),
    layers.Dense(64, activation="relu"),
    layers.Dense(10, activation="softmax")
])

# Compile model
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# Show architecture
model.summary()

# Train model
history = model.fit(
    x_train,
    y_train,
    epochs=5,
    validation_split=0.2
)

# Evaluate model
test_loss, test_accuracy = model.evaluate(x_test, y_test)

print("\nFinal Test Loss:", test_loss)
print("Final Test Accuracy:", test_accuracy)

# Predict first test image
prediction = model.predict(x_test[:1])
predicted_digit = prediction.argmax()

print("\nPredicted Digit:", predicted_digit)
print("Actual Digit:", y_test[0])
