import numpy as np
import time
import h5py
import matplotlib.pyplot as plt

from scipy.stats import linregress

import os
from datetime import datetime

interval = 0.05 # 0.05
x1_max = 8
Vin = np.arange(-x1_max, x1_max+interval, interval)
print("len", len(Vin))


s = np.random.uniform(-3, 3, 100)

print(s)
fig = plt.figure()
plt.plot(s, 'x')
# plt.close(fig)
plt.show()


# fin
