"""Loss functions for measuring prediction error."""

import numpy as np


def mse_loss(actual_output, predicted_output):
    """Calculate Mean Squared Error loss.

    The actual output is the correct target value from the dataset.
    The predicted output is the value produced by the neural network.

    Lower loss means predictions are getting closer to the actual outputs.
    After training, this value should decrease.
    """
    return np.mean((actual_output - predicted_output) ** 2)
