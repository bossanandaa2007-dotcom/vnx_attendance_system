"""Utility functions for the neural network forward pass project."""

import numpy as np


def sigmoid(values):
    """Apply sigmoid activation to a number or NumPy array.

    Sigmoid converts raw values into a range between 0 and 1, which is useful
    for interpreting the final output as a probability-like prediction.
    """
    return 1 / (1 + np.exp(-values))


def pretty_print(title, values, show_shape=True):
    """Print a title, matrix values, and optionally the matrix shape."""
    print(f"{title}:")
    print(values)

    if show_shape:
        print(f"Shape: {values.shape}")

    print()
