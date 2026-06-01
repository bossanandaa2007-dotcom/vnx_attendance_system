"""A 2-layer neural network trained manually with NumPy."""

import numpy as np

from activation import sigmoid, sigmoid_derivative
from loss import mse_loss


class NeuralNetwork:
    """Simple neural network for learning the XOR pattern.

    Architecture:
        Input layer: 2 neurons
        Hidden layer: 3 neurons
        Output layer: 1 neuron
    """

    def __init__(self, learning_rate=0.5, random_seed=42):
        """Initialize weights, biases, and training settings."""
        if learning_rate <= 0:
            raise ValueError("learning_rate must be greater than 0.")

        self.learning_rate = learning_rate
        rng = np.random.default_rng(random_seed)

        self.input_hidden_weights = rng.uniform(low=-1.0, high=1.0, size=(2, 3))
        self.hidden_output_weights = rng.uniform(low=-1.0, high=1.0, size=(3, 1))

        self.hidden_bias = np.zeros((1, 3))
        self.output_bias = np.zeros((1, 1))

        self.hidden_input = None
        self.hidden_output = None
        self.final_input = None
        self.predicted_output = None

    def print_parameter_shapes(self):
        """Print matrix shapes to make layer dimensions easy to understand."""
        print("Matrix Shapes:")
        print(f"  Input-Hidden Weights:  {self.input_hidden_weights.shape}")
        print(f"  Hidden Bias:           {self.hidden_bias.shape}")
        print(f"  Hidden-Output Weights: {self.hidden_output_weights.shape}")
        print(f"  Output Bias:           {self.output_bias.shape}")
        print()

    def forward(self, input_data):
        """Run forward propagation and return the predicted output.

        Flow:
            Input
             -> hidden layer calculation
             -> sigmoid activation
             -> output layer calculation
             -> sigmoid prediction
        """
        self.hidden_input = np.dot(input_data, self.input_hidden_weights)
        self.hidden_input += self.hidden_bias
        self.hidden_output = sigmoid(self.hidden_input)

        self.final_input = np.dot(self.hidden_output, self.hidden_output_weights)
        self.final_input += self.output_bias
        self.predicted_output = sigmoid(self.final_input)

        return self.predicted_output

    def backward(self, input_data, actual_output):
        """Perform backpropagation and update weights and biases.

        This method manually calculates output error, output gradient,
        hidden error, and hidden gradient before applying gradient descent.
        """
        sample_count = input_data.shape[0]

        output_error = self.predicted_output - actual_output
        output_gradient = output_error * sigmoid_derivative(self.predicted_output)

        hidden_error = np.dot(output_gradient, self.hidden_output_weights.T)
        hidden_gradient = hidden_error * sigmoid_derivative(self.hidden_output)

        hidden_output_weight_gradient = np.dot(
            self.hidden_output.T,
            output_gradient,
        ) / sample_count
        output_bias_gradient = np.mean(output_gradient, axis=0, keepdims=True)

        input_hidden_weight_gradient = np.dot(
            input_data.T,
            hidden_gradient,
        ) / sample_count
        hidden_bias_gradient = np.mean(hidden_gradient, axis=0, keepdims=True)

        self.hidden_output_weights -= (
            self.learning_rate * hidden_output_weight_gradient
        )
        self.output_bias -= self.learning_rate * output_bias_gradient
        self.input_hidden_weights -= self.learning_rate * input_hidden_weight_gradient
        self.hidden_bias -= self.learning_rate * hidden_bias_gradient

    def train(self, input_data, actual_output, epochs=10000, log_epochs=None):
        """Train the network for a fixed number of epochs."""
        if epochs <= 0:
            raise ValueError("epochs must be greater than 0.")

        if input_data.ndim != 2 or input_data.shape[1] != 2:
            raise ValueError("input_data must have shape (samples, 2).")

        if actual_output.ndim != 2 or actual_output.shape[1] != 1:
            raise ValueError("actual_output must have shape (samples, 1).")

        if input_data.shape[0] != actual_output.shape[0]:
            raise ValueError("input_data and actual_output sample counts must match.")

        log_epochs = set(log_epochs or [])
        final_loss = None

        for epoch in range(1, epochs + 1):
            predictions = self.forward(input_data)
            self.backward(input_data, actual_output)
            final_loss = mse_loss(actual_output, predictions)

            if epoch in log_epochs:
                print(f"Epoch {epoch:5d} Loss: {final_loss:.6f}")

        return final_loss
