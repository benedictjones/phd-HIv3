from mod_software.SI import si
import numpy as np
import time
import h5py
import matplotlib.pyplot as plt
from tqdm import tqdm

from scipy.stats import linregress

import os
from datetime import datetime



obj = si(Rshunt=14000)  # , electrode3='in'

Rshunt = obj.Rshunt

# #################################
now = datetime.now()
real_d_string = now.strftime("%d_%m_%Y")
d_string = now.strftime("%Y_%m_%d")
print("Date:", real_d_string)
print("Date:", d_string)
t_string = now.strftime("%H_%M_%S")
print("Time Stamp:", t_string, "\n\n")



p = 1
OP = 4

test_label = 'Noise_Test'
save_dir = "Results/%s/%s_%s" % (d_string, t_string, test_label)
os.makedirs(save_dir)

# ################################


interval = 0.1 # 0.05, 0.025 #  DAC-QE~0.0005, ADC-QE~0.002V
x1_max = 9 # 3.5, 3
Vin = np.arange(-x1_max, x1_max+interval, interval)

num_sets = len(Vin)

Vout = []
Iout = []

obj.ElectrodeState()

input("Press Enter to continue... ")



V_loop = []
Std_loop = []


tic = time.time()
for v in tqdm(Vin):

    # # Set Voltage
    # v = np.round(v,3)
    obj.SetV(electrode=p, voltage=v)

    # # Perform one long capture to get DeBug plot
    # obj.ReadVoltage(OP, debug=0, nSamples=20)  # ret_type = 'raw', | ch0, pin3, op1

    # print("Set voltage on pin %d to %fV" % (p, v))

    # # Repeat for a number of repetitions
    # input("Press Enter to move to next input V")

t = time.time() - tic
print("Time to complete %d sets = %f" % (num_sets, t))

# # Vary whether the spi or set pi is active to see what is slow

obj.fin()


# exit()

#

#
