# Neural Network Forward Pass using NumPy

This beginner-friendly project demonstrates how a simple feedforward neural
network performs one complete forward pass using only Python and NumPy.

## Topics Covered

- Neurons
- Weights
- Bias
- Forward Propagation
- Sigmoid Activation

## Neural Network Architecture

The network contains:

- Input Layer: 2 input features
- Hidden Layer: 3 neurons
- Output Layer: 1 neuron

Flow:

```text
Input -> Hidden Layer -> Output Layer
```

## Project Structure

```text
Day_1_NN_Forward_Pass/
|-- nn_forward.py
|-- utils.py
|-- config.py
|-- requirements.txt
|-- README.md
```

## File Descriptions

`nn_forward.py`

Main runnable file. It creates a sample input, performs the forward pass, and
prints the intermediate and final results.

`utils.py`

Contains helper functions:

- `sigmoid()` for activation
- `pretty_print()` for clean output formatting

`config.py`

Stores all manually selected weights and biases separately from the main logic.

`requirements.txt`

Lists the only required external package:

```text
numpy
```

## How to Run

Open a terminal inside this folder:

```bash
cd Week_5_ML/Day_1_NN_Forward_Pass
```

Install the required package:

```bash
pip install -r requirements.txt
```

Run the project:

```bash
python nn_forward.py
```

## Expected Output Style

```text
================================
NEURAL NETWORK FORWARD PASS
================================

Input:
[[5 7]]
Shape: (1, 2)

Hidden Layer Raw:
...

Hidden Layer Activated:
...

Final Prediction:
[[0.xx]]

================================
```

## Learning Outcome

After completing this practical, you should understand how input data moves
through a basic neural network. You will see how weights and biases create raw
values, how the sigmoid activation function transforms those values, and how a
final prediction is produced without using any machine learning framework.
