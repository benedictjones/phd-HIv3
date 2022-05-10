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



x = np.arange(-1,0,0.1)
y = np.arange(0,2,0.1)

xv, yv = np.meshgrid(x, y)
print(np.shape(xv))
Vo = np.zeros(np.shape(xv))
print("Shape Vo:", np.shape(Vo))
for i in range(len(x)):
    for j in range(len(y)):
        Vo[j, i] = xv[j,i] + yv[j,i]**2

fig = plt.figure()
plt.imshow(Vo, extent=[np.min(x), np.max(x), np.min(y), np.max(y)], origin='lower')
plt.colorbar()

plt.show()


# fin
