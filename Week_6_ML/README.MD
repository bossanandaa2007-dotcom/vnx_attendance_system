# Week 6 Monday - MNIST Dense Neural Network

## Goal

Build a dense neural network using TensorFlow and Keras to classify handwritten digits from the MNIST dataset.

## Dataset

MNIST contains handwritten digit images from 0 to 9.

- Training images: 60,000
- Testing images: 10,000
- Image size: 28 × 28
- Image type: Grayscale

## Tech Stack

- Python
- TensorFlow
- Keras
- NumPy
- Matplotlib

## Model Architecture

Input image: 28 × 28

The image is flattened into 784 values.

Architecture:

```text
Input Image: 28 × 28
↓
Flatten: 784 values
↓
Dense: 128 neurons + ReLU
↓
Dense: 64 neurons + ReLU
↓
Dense: 10 neurons + Softmax
↓
Output: Digit probabilities from 0 to 9