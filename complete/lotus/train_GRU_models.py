import csv
from collections import defaultdict
from datetime import datetime
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt

# Define the GRU model
class GRU(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(GRU, self).__init__()
        self.gru = nn.GRU(input_size, hidden_size)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x, _ = self.gru(x.unsqueeze(0))
        x = self.fc(x[-1])
        return x


def train_nasa(data):
    # Prepare data

    data = data.reshape(-1, 1)

    # Normalize data
    mean = data.mean()
    std = data.std()
    data = (data - mean) / std

    # Split data into training and testing sets
    split_index = int(0.6 * len(data))
    train_data = data[:split_index]
    train_data_un_normalised = train_data
    test_data = data[split_index:]
    test_targets = data[split_index:]

    # Convert data to tensors
    train_data = torch.FloatTensor(train_data)
    test_data = torch.FloatTensor(test_data)
    test_targets = torch.FloatTensor(test_targets)
    # Initialize the model, loss function, and optimizer
    model = GRU(1, 128, 1)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Train the model
    for epoch in range(200):
        optimizer.zero_grad()
        outputs = model(train_data)
        loss = criterion(outputs, train_data)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 20 == 0:
            print(f"NASA Model -> Epoch: {epoch + 1}, Loss: {loss.item()}")

    # Save the model
    torch.save(model.state_dict(), "NASA_MODEL.pth")

    # Make predictions for the entire testing data
    with torch.no_grad():
        test_outputs = model(test_data)

    # Convert predictions and actual counts to numpy arrays
    test_outputs = test_outputs.squeeze().numpy()
    test_targets = test_targets.numpy()

    # Plot the predictions and actual counts
    plt.plot(test_targets, label="Actual Count")
    plt.plot(test_outputs, label="Predicted Count")
    plt.legend()
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.title("Predicted vs Actual Counts")
    plt.savefig('nasa_image.png')


def train_WorldCup(data):
    # Prepare data

    data = data.reshape(-1, 1)

    # Normalize data
    mean = data.mean()
    std = data.std()
    data = (data - mean) / std

    # Split data into training and testing sets
    split_index = int(0.6 * len(data))
    train_data = data[:split_index]
    train_data_un_normalised = train_data
    test_data = data[split_index:]
    test_targets = data[split_index:]

    # Convert data to tensors
    train_data = torch.FloatTensor(train_data)
    test_data = torch.FloatTensor(test_data)
    test_targets = torch.FloatTensor(test_targets)
    # Initialize the model, loss function, and optimizer
    model = GRU(1, 128, 1)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Train the model
    for epoch in range(200):
        optimizer.zero_grad()
        outputs = model(train_data)
        loss = criterion(outputs, train_data)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 20 == 0:
            print(f"World Cup Model -> Epoch: {epoch + 1}, Loss: {loss.item()}")

    # Save the model
    torch.save(model.state_dict(), "wc_model_count.pth")

    # Make predictions for the entire testing data
    with torch.no_grad():
        test_outputs = model(test_data)

    # Convert predictions and actual counts to numpy arrays
    test_outputs = test_outputs.squeeze().numpy()
    test_targets = test_targets.numpy()
    # Plot the predictions and actual counts
    plt.figure(figsize=(8, 6))
    plt.plot(test_targets, label="Actual Count")
    plt.plot(test_outputs, label="Predicted Count")
    plt.legend()
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.title("Predicted vs Actual Counts")
    plt.savefig('world_cup_image.png')
