# Neural Network Backpropagation From Scratch

This practical session builds and trains a 2-layer neural network manually using only Python and NumPy. It demonstrates how a model learns the XOR pattern through forward propagation, loss calculation, backpropagation, gradient descent, and weight updates.

## Concepts Learned

- Artificial Neural Network
- Forward Propagation
- Loss Function
- Backpropagation
- Gradient Descent
- Weight Optimization

## Architecture Diagram

```text
Input Layer (2)
      |
      v
Hidden Layer (3)
      |
      v
Output Layer (1)
```

## Mathematical Concepts

Each neuron calculates a weighted sum and adds a bias:

```text
z = wx + b
```

The sigmoid activation function converts this value into a prediction-friendly range between 0 and 1:

```text
sigmoid(x) = 1 / (1 + e^-x)
```

Weights are updated using gradient descent:

```text
new weight = old weight - learning_rate * gradient
```

Mean Squared Error compares the actual output with the predicted output:

```text
MSE = mean((actual output - predicted output)^2)
```

As training improves the network, the loss decreases.

## Project Files

- `activation.py` - sigmoid activation and derivative functions
- `loss.py` - Mean Squared Error loss function
- `neural_network.py` - neural network class with forward pass, backpropagation, and training loop
- `train.py` - XOR dataset, training execution, and formatted output
- `requirements.txt` - required Python package

## How To Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the training script:

```bash
python train.py
```

## Expected Output

```text
================================
NEURAL NETWORK TRAINING
================================

Before Training:
[[0.xx]
 [0.xx]
 [0.xx]
 [0.xx]]

Training Started...

Epoch  1000 Loss: ...
Epoch  5000 Loss: ...
Epoch 10000 Loss: ...

After Training:
[[0.05]
 [0.95]
 [0.95]
 [0.05]]

Final Loss:
0.00xx
================================
```

## Learning Outcome

This project demonstrates how neural networks learn internally without TensorFlow, PyTorch, Scikit-learn, or any other machine learning framework. By implementing every calculation manually with NumPy, you can clearly see how predictions, errors, gradients, and weight updates work together during training.
