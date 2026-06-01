
#This file stores the manually selected weights and biases separately so the main program can focus on the forward propagation steps.


import numpy as np


# Weights from the input layer to the hidden layer.
# Shape: (number of input features, number of hidden neurons) = (2, 3)
INPUT_TO_HIDDEN_WEIGHTS = np.array(
    [
        [0.10, 0.20, 0.30],
        [0.40, 0.50, 0.60],
    ]
)

# Bias values for the hidden layer.
# Shape: (1, number of hidden neurons) = (1, 3)
HIDDEN_BIAS = np.array([[0.10, 0.20, 0.30]])

# Weights from the hidden layer to the output layer.
# Shape: (number of hidden neurons, number of output neurons) = (3, 1)
HIDDEN_TO_OUTPUT_WEIGHTS = np.array(
    [
        [0.70],
        [0.80],
        [0.90],
    ]
)

# Bias value for the output layer.
# Shape: (1, number of output neurons) = (1, 1)
OUTPUT_BIAS = np.array([[0.50]])
