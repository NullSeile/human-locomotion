import numpy as np
import matplotlib.pyplot as plt

plt.hist(np.random.normal(scale=0.5 * 2, size=10000))
plt.show()
