"""Neural Network Forward Pass using NumPy.

This script demonstrates one complete forward pass through a small feedforward
neural network:

Input Layer: 2 features
Hidden Layer: 3 neurons
Output Layer: 1 neuron
"""

import numpy as np

from config import (
    HIDDEN_BIAS,
    HIDDEN_TO_OUTPUT_WEIGHTS,
    INPUT_TO_HIDDEN_WEIGHTS,
    OUTPUT_BIAS,
)
from utils import pretty_print, sigmoid


def main():
    """Run one forward pass through the neural network."""
    print("================================")
    print("NEURAL NETWORK FORWARD PASS")
    print("================================")
    print()

    # Step 1: Create the sample input.
    # X has 1 row because we are passing one example through the network.
    # X has 2 columns because the network expects 2 input features.
    x = np.array([[5, 7]])
    pretty_print("Input", x)

    # Step 2: Calculate raw hidden layer values.
    # Formula: hidden_raw = input dot hidden_weights + hidden_bias
    # Result shape: (1, 2) dot (2, 3) + (1, 3) = (1, 3)
    hidden_raw = np.dot(x, INPUT_TO_HIDDEN_WEIGHTS) + HIDDEN_BIAS
    pretty_print("Hidden Layer Raw", hidden_raw)

    # Step 3: Apply sigmoid activation to the hidden layer.
    # This converts raw hidden values into activated values between 0 and 1.
    hidden_activated = sigmoid(hidden_raw)
    pretty_print("Hidden Layer Activated", hidden_activated)

    # Step 4: Calculate raw output layer value.
    # Formula: output_raw = hidden_activated dot output_weights + output_bias
    # Result shape: (1, 3) dot (3, 1) + (1, 1) = (1, 1)
    output_raw = np.dot(hidden_activated, HIDDEN_TO_OUTPUT_WEIGHTS) + OUTPUT_BIAS
    pretty_print("Output Layer Raw", output_raw)

    # Step 5: Apply sigmoid activation to produce the final prediction.
    # The final value is between 0 and 1.
    final_prediction = sigmoid(output_raw)
    pretty_print("Final Prediction", final_prediction)

    print("================================")


if __name__ == "__main__":
    main()
