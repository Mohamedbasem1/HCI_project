# src/utils.py

import numpy as np


def load_template(path):
    """Load exercise template from a file."""
    return np.load(path)
