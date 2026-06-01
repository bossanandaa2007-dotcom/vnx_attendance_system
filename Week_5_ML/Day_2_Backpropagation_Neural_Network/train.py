"""Train a neural network on the XOR dataset using only NumPy."""

import numpy as np

from loss import mse_loss
from neural_network import NeuralNetwork


def print_predictions(title, predictions):
    """Print predictions in a clean portfolio-friendly format."""
    print(title)
    print(np.round(predictions, 2))
    print()


def main():
    """Create data, train the model, and display results."""
    xor_input = np.array(
        [
            [0, 0],
            [0, 1],
            [1, 0],
            [1, 1],
        ],
        dtype=float,
    )

    xor_output = np.array(
        [
            [0],
            [1],
            [1],
            [0],
        ],
        dtype=float,
    )

    model = NeuralNetwork(learning_rate=1.0, random_seed=7)

    print("=" * 32)
    print("NEURAL NETWORK TRAINING")
    print("=" * 32)
    print()

    print("Dataset Shapes:")
    print(f"  Input Data:    {xor_input.shape}")
    print(f"  Actual Output: {xor_output.shape}")
    print()
    model.print_parameter_shapes()

    before_training = model.forward(xor_input)
    print_predictions("Before Training:", before_training)

    print("Training Started...")
    print()
    final_loss = model.train(
        xor_input,
        xor_output,
        epochs=10000,
        log_epochs=[1000, 5000, 10000],
    )
    print()

    after_training = model.forward(xor_input)
    final_loss = mse_loss(xor_output, after_training)

    print_predictions("After Training:", after_training)
    print("Final Loss:")
    print(f"{final_loss:.6f}")
    print()
    print("=" * 32)


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"Input Error: {error}")
