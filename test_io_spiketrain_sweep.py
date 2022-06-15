from mod_software.SI import si
import numpy as np
import time
import h5py
import matplotlib.pyplot as plt
from tqdm import tqdm

from scipy.stats import linregress

import os
from datetime import datetime


ADCfclk = 2000000 # 2000000
obj = si(Rshunt=100000, ADCspeed=ADCfclk)  # 14000 , 47000, , electrode11='in'

Rshunt = obj.Rshunt
num_sweeps = 6


# #################################
now = datetime.now()
real_d_string = now.strftime("%d_%m_%Y")
d_string = now.strftime("%Y_%m_%d")
print("Date:", real_d_string)
print("Date:", d_string)
t_string = now.strftime("%H_%M_%S")
print("Time Stamp:", t_string, "\n\n")


p = 1
OP = 4 # 4

#test_label = 'IO_sweep_%s__p%s_Op%d' % (type,p,OP)
test_label = 'PKs__%s__p%s_Op%d' % ('SpikeT',p,OP)
#test_label = 'CustomDRN_%s__Op%d' % (type,OP)

save_dir = "Results/%s/%s_%s" % (d_string, t_string, test_label)
os.makedirs(save_dir)

# ################################


interval = 0.025 # 0.05 #  DAC-QE~0.0005, ADC-QE~0.002V
x1_max = 9 # 3.5, 3
Vin = np.arange(-x1_max, x1_max+interval, interval)  # neg to pos

Vin = np.arange(0, x1_max+interval, interval)  # zero to pos
#Vin = np.arange(-x1_max, 0+interval, interval)  # neg to zero

#Vin = np.arange(0, 3+interval, interval)  # x1_max

direction = 'forward_single' # forward, backward, random

if direction == 'forward' :
    Vin_sweep = np.concatenate((Vin, np.flip(Vin)))
elif direction == 'backward' :
    Vin_sweep = np.concatenate((np.flip(Vin), Vin))
elif direction == 'random':
    Vin_sweep = np.random.uniform(-x1_max, x1_max, 800)

elif direction == 'forward_single':
    Vin_sweep = Vin
elif direction == 'backward_single':
    Vin_sweep = np.flip(Vin)

print("Num write/reads:", num_sweeps*len(Vin_sweep))



obj.ElectrodeState()

input("Press Enter to start sweeps... ")

input_pairs = [[1,1]]
ops = [1,2]
record = obj.SetV_spike_train(input_pairs, ops)


obj.fin()


# save data
location = "%s/data.hdf5" % (save_dir)
with h5py.File(location, 'a') as hdf:

    G_in = hdf.create_group("Ins")
    for in_pair in input_pairs:
        electrode, inst = in_pair
        G_in.create_dataset('electrode_%d' % (electrode), data=record['electrode_%d' % (electrode)])

    G_op = hdf.create_group("Ops")
    for op in ops:
        G_op.create_dataset('op_%d' % (op), data=record['op_%d' % (op)])

#

#

fig, axs = plt.subplots(2, sharex=True)

for in_pair in input_pairs:
    electrode, inst = in_pair
    zipped = record['electrode_%d' % (electrode)]
    t, st = list(zip(*zipped))
    axs[0].plot(t, st, label="in%d" % (electrode))
axs[0].legend()
axs[0].ylabel('Input Voltage Spikes')

for op in ops:
    zipped = record['op_%d' % (op)]
    t, Vo = list(zip(*zipped))
    axs[1].plot(t, Vo, label="op%d" % (op))
axs[1].legend()
axs[1].xlabel('Time')
axs[1].ylabel('Voltage')

fig_path = "%s/FIG_Vd_vs_Iout.png" % (save_dir)
fig.savefig(fig_path, dpi=200)

#

plt.show()
plt.close('all')



# fin
