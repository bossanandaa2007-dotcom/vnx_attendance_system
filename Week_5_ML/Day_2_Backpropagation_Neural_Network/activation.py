"""Activation functions used by the neural network."""

import numpy as np


def sigmoid(x):
    """Return the sigmoid activation for the given input.

    Activation functions help a neural network learn non-linear patterns.
    Without them, multiple layers would behave like one simple linear model.

    Formula:
        sigmoid(x) = 1 / (1 + e^(-x))
    """
    return 1 / (1 + np.exp(-x))


def sigmoid_derivative(activated_value):
    """Return the derivative of sigmoid from its activated output.

    During backpropagation, derivatives tell us how strongly each neuron
    contributed to the final prediction error.
    """
    return activated_value * (1 - activated_value)
