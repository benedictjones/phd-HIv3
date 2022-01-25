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

test_label = 'Test_calibrate_P%d_to_OP%d' % (p, OP)
save_dir = "Results/%s/%s_%s" % (d_string, t_string, test_label)
os.makedirs(save_dir)

# ################################


Vin_sweep = [-3, -1, 0, 1, 3]
# Vin_sweep = [-9, -4, 0, 4, 8, 9]

"""
interval = 0.1 # 0.05
x1_max = 9
Vin_sweep = np.arange(-x1_max, x1_max+interval, interval)
#"""

Vout = []
Iout = []

obj.ElectrodeState()

input("Press Enter to continue... ")


Vdiff = []
Vouts = []

for v in Vin_sweep:
    print("\n")
    v = np.round(v,3)

    obj.SetVoltage(electrode=p, voltage=v)

    Vop = obj.ReadVoltage(OP, debug=1)  # ch0, pin3, op1

    Vd = v - Vop
    print("Vin:", v, ", Vout:", Vop, " | Vdiff:", Vd)
    Vdiff.append(Vd)
    Vouts.append(Vop)
    input("Press Enter to move to next input V")

print("\nMean diff:", np.mean(Vdiff))

obj.fin()

exit()



# # save data
location = "%s/data.hdf5" % (save_dir)
with h5py.File(location, 'a') as hdf:
    G_sub = hdf.create_group("IO")

    G_sub.create_dataset('Vin', data=Vin_sweep)
    G_sub.create_dataset('Vout', data=Vout)
    G_sub.create_dataset('Vdiff', data=Vdiff)





# # Plot data
fig = plt.figure()
plt.plot(Vin_sweep, Vouts, label='V')
plt.legend()
plt.xlabel('Vin')
plt.ylabel('Vout')
plt.title('Voltage sweep being directly read')
fig_path = "%s/FIG_VinVout.png" % (save_dir)
fig.savefig(fig_path, dpi=300)


reg = linregress(x=Vin_sweep, y=Vdiff)
print("x(Vin) y(Vdiff) slope:", reg.slope)

fig = plt.figure()
plt.plot(Vin_sweep, Vdiff, 'o', label='V')
plt.legend()
plt.xlabel('Vin')
plt.ylabel('Vdiff = Vin - Vout')
plt.title('Voltage sweep being directly read\nGrad=%f' % (reg.slope))
fig_path = "%s/FIG_VinVdiff.png" % (save_dir)
fig.savefig(fig_path, dpi=300)



plt.show()
