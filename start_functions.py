import numpy as np

def double_gauss_func(d, x):
    sigma = 0.9 + 0.03 * d
    b = 3 * sigma
    shift2 = 10 - 2 * b
    return (np.exp(-0.5 * np.power(((x - b) / sigma), 2.0)) +
            np.exp(-0.5 * np.power(((x - b - shift2) / sigma), 2.0)))


def gauss_func(d, x):
    sigma = 0.4 + 0.16 * d
    b = 5
    return (np.exp(-0.5 * np.power(((x - b) / sigma), 2.0)))


def step_func(d, x):
    left = 4 - 0.3 * d
    right = 6 + 0.3 * d
    return np.where((left <= x) & (x <= right), 1.0, 0.0)


def triangle_func(d, x):
    k = 0.25 - 0.0125 * d
    b = -0.75 + 0.0625 * d
    #return (k * x + b if 0 <= k * x + b <= 1 else 0)
    return np.where((0 <= k * x + b) & (k * x + b <= 1), k * x + b, 0.0)
