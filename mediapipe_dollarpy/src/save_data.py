import numpy as np

def save_data(data, filename):
    np.save(filename, data)
    print(f"Data saved to {filename}")

def load_data(filename):
    return np.load(filename)