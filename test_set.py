from mod_software.SI import si
import numpy as np
import time
import h5py
import matplotlib.pyplot as plt

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


Vin_sweep = [-5, 0, 5]


Vout = []
Iout = []

obj.ElectrodeState()

input("Press Enter to continue... ")



smaple_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 22, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 125, 140, 150, 175, 200, 225, 250, 275, 300, 350, 400, 450, 500]
smaple_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 22, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 125, 140, 150, 175, 200]
smaple_list = np.arange(1,50,1)

V_loop = []
Std_loop = []

for v in Vin_sweep:

    # # Set Voltage
    v = np.round(v,3)
    obj.SetVoltage(electrode=p, voltage=v)

    # # Perform one long capture to get DeBug plot
    obj.ReadVoltage(OP, debug=0, nSamples=20)  # ret_type = 'raw', | ch0, pin3, op1

    print("Set voltage on pin %d to %fV" % (p, v))

    # # Repeat for a number of repetitions
    input("Press Enter to move to next input V")


obj.fin()


# exit()

#

#

