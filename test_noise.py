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
    # obj.ReadVoltage(OP, debug=1, nSamples=1000, raw=1)  # ch0, pin3, op1

    # # Repeat for a number of repetitions
    V_rep = []
    Std_rep = []
    for rep in range(3):

        # # Run though all samples to get data
        V_list = []
        std_list = []
        for nS in smaple_list:
            Vop, std = obj.ReadVoltage(OP, debug=0, nSamples=nS, raw=1)  # ch0, pin3, op1
            V_list.append(Vop)
            std_list.append(std)
        V_rep.append(V_list)
        Std_rep.append(std_list)

    V_loop.append(V_rep)
    Std_loop.append(Std_rep)


obj.fin()


# exit()

#

#

# # save data
location = "%s/data.hdf5" % (save_dir)
with h5py.File(location, 'a') as hdf:

    for i, Vin in enumerate(Vin_sweep):
        G_sub = hdf.create_group("Vin_%.4f" % (Vin))
        G_sub.create_dataset('sample_size', data=smaple_list)

        Vrep = V_loop[i]
        Stdrep = Std_loop[i]
        for r in range(3):
            G_rep = G_sub.create_group("rep_%d" % (r))
            G_rep.create_dataset('Vout', data=Vrep[r])
            G_rep.create_dataset('std', data=Stdrep[r])

#

#

#

# # Plot Mean vs sample size
ms = ['o', '+', '*']
for i, Vin in enumerate(Vin_sweep):
    fig = plt.figure()
    Vrep = V_loop[i]
    Stdrep = Std_loop[i]

    for r in range(3):
        plt.plot(smaple_list, Vrep[r], marker=ms[r], label='Rep=%d' % (r))
    plt.legend()
    plt.xlabel('Sample Size')
    plt.ylabel('mean adc voltage')
    plt.title('Sweeping sample size against MEAN Vout (Vin=%f)' % (Vin))
    fig_path = "%s/FIG_mean_Vin%d.png" % (save_dir, Vin)
    fig.savefig(fig_path, dpi=300)

# # Plot Std vs sample size
for i, Vin in enumerate(Vin_sweep):
    fig = plt.figure()
    Vrep = V_loop[i]
    Stdrep = Std_loop[i]

    for r in range(3):
        plt.plot(smaple_list, Stdrep[r], marker=ms[r], label='Rep=%d' % (r))
    plt.legend()
    plt.xlabel('Sample Size')
    plt.ylabel('std adc voltage')
    plt.title('Sweeping sample size against STD Vout (Vin=%f)' % (Vin))
    fig_path = "%s/FIG_std_Vin%d.png" % (save_dir, Vin)
    fig.savefig(fig_path, dpi=300)

#

# # Plot std vs sample size
fig = plt.figure()
for i, Stdrep in enumerate(Std_loop):
    for r in range(3):
        plt.plot(smaple_list, Stdrep[r], marker=ms[r], label='Rep=%d' % (r))
plt.legend()
plt.xlabel('Sample Size')
plt.ylabel('Std')
plt.title('Sweeping sample size against std')
fig_path = "%s/FIG_STDvSampleSizeout.png" % (save_dir)
fig.savefig(fig_path, dpi=300)

#

# # Plot mean vs sample size
fig, ax = plt.subplots()
fig.subplots_adjust(right=0.75)

plt.title('Sweeping sample size against Read Voltage')

twin1 = ax.twinx()
twin2 = ax.twinx()

# Offset the right spine of twin2.  The ticks and label have already been
# placed on the right by twinx above.
# twin2.spines.right.set_position(("axes", 1.2))  # causes error
twin2.spines['right'].set_position(("axes", 1.2))

for r in range(3):
    p1, = ax.plot(smaple_list, V_loop[0][r], "bo", label='V=%.4f' % (Vin_sweep[0]))

for r in range(3):
    p2, = twin1.plot(smaple_list, V_loop[1][r], "r+", label='V=%.4f' % (Vin_sweep[1]))

for r in range(3):
    p3, = twin2.plot(smaple_list, V_loop[2][r], "g*", label='V=%.4f' % (Vin_sweep[2]))

#ax.set_xlim(0, 2)
#ax.set_ylim(0, 2)
#twin1.set_ylim(0, 4)
#twin2.set_ylim(1, 65)

ax.set_xlabel("Sample Size")
ax.set_ylabel("Mean V")
twin1.set_ylabel("Mean V")
twin2.set_ylabel("Mean V")

ax.yaxis.label.set_color(p1.get_color())
twin1.yaxis.label.set_color(p2.get_color())
twin2.yaxis.label.set_color(p3.get_color())

tkw = dict(size=4, width=1.5)
ax.tick_params(axis='y', colors=p1.get_color(), **tkw)
twin1.tick_params(axis='y', colors=p2.get_color(), **tkw)
twin2.tick_params(axis='y', colors=p3.get_color(), **tkw)
ax.tick_params(axis='x', **tkw)

ax.legend(handles=[p1, p2, p3])

fig_path = "%s/FIG_VOPvSampleSizeout.png" % (save_dir)
fig.savefig(fig_path, dpi=300)



plt.show()
