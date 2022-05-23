import matplotlib.pyplot as plt
import argparse

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
args = parser.parse_args()

with open(args.file, "r") as file:

    avg_vals = list()
    max_vals = list()

    for i, line in enumerate(file):
        vals = np.array([float(v) for v in line.split(" ")])

        avg_vals.append(np.mean(vals))
        max_vals.append(np.max(vals))

    plt.plot(avg_vals, label="avg")
    plt.plot(max_vals, label="max")

    plt.tight_layout()

    plt.show()
