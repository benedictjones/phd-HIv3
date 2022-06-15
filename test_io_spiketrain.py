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


obj.ElectrodeState()

input("Press Enter to start sweeps... ")

for inst in [-1, -0.5, -0.2, -0.1, -0.05, 0.05, 0.1, 0.2, 0.5, 1]:

    print("Measuring spike train input for:", inst)
    input_pairs = [[p,inst]]
    ops = [OP]
    record = obj.SetV_spike_train(input_pairs, ops, encoding='rate')


    


    # save data
    location = "%s/data.hdf5" % (save_dir)
    with h5py.File(location, 'a') as hdf:

        G = hdf.create_group("Instance_%.3f" % (inst))
        
        G_in = G.create_group("In")
        for in_pair in input_pairs:
            electrode, inst = in_pair
            G_in.create_dataset('electrode_%d' % (electrode), data=record['electrode_%d' % (electrode)])

        G_op = G.create_group("Ops")
        for op in ops:
            G_op.create_dataset('op_%d' % (op), data=record['op_%d' % (op)])

    #

    #

    fig, axs = plt.subplots(2, sharex=True)

    axs[0].set_title("Responce to input instance %.3f" % (inst))

    for in_pair in input_pairs:
        electrode, inst = in_pair
        zipped = record['electrode_%d' % (electrode)]
        t, st = list(zip(*zipped))
        axs[0].plot(t, st, '-x', label="in%d" % (electrode))
    axs[0].legend()
    axs[0].set_ylabel('Input Voltage Spikes')

    for op in ops:
        zipped = record['op_%d' % (op)]
        t, Vo = list(zip(*zipped))
        axs[1].plot(t, Vo, '-x', label="op%d" % (op))
    axs[1].legend()
    axs[1].set_xlabel('Time')
    axs[1].set_xlabel('Voltage')

    fig_path = "%s/FIG_spike_responce__%s.png" % (save_dir, str(inst))
    fig.savefig(fig_path, dpi=200)
    plt.close(fig)
#

plt.show()
plt.close('all')

obj.fin()

# fin
