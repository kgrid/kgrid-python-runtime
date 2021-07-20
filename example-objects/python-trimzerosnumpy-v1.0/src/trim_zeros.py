import numpy as np


def trim_zeros(json_input):
    arr = np.asarray(json_input['array'], dtype=object)
    return np.trim_zeros(arr).tolist()
