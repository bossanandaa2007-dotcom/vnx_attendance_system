1, # Week 6 Monday - MNIST Dense Neural Network

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

---------------------------------------------------------------------------------------

2, # Week 6 Day 2 - Fashion MNIST Loss Curves and Overfitting Analysis

## Goal

The goal of this project is to train a dense neural network on the Fashion MNIST dataset and analyze the training behavior using loss curves and accuracy curves.

## Dataset

Fashion MNIST contains grayscale images of clothing items.

- Training images: 60,000
- Testing images: 10,000
- Image size: 28 × 28
- Image type: Grayscale
- Number of classes: 10

## Classes

1. T-shirt/top
2. Trouser
3. Pullover
4. Dress
5. Coat
6. Sandal
7. Shirt
8. Sneaker
9. Bag
10. Ankle boot

## Tech Stack

- Python
- TensorFlow
- Keras
- NumPy
- Matplotlib

## Model Architecture

```text
Input Image: 28 × 28
↓
Flatten Layer: 784 values
↓
Dense Layer: 256 neurons + ReLU
↓
Dense Layer: 128 neurons + ReLU
↓
Dense Layer: 10 neurons + Softmax
↓
Output: Probability for 10 clothing classes