from mod_software.SI import si
import numpy as np
import time
import h5py
import matplotlib.pyplot as plt

from scipy.stats import linregress

import os
from datetime import datetime



obj = si(Rshunt=14000)  # 14000

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

test_label = 'IO_Triangle_sweep__p%s_Op%d' % (p,OP)

save_dir = "Results/%s/%s_%s" % (d_string, t_string, test_label)
os.makedirs(save_dir)

# ################################


interval = 0.01 # 0.05
x1_max = 3.5
Vin = np.arange(-x1_max, x1_max+interval, interval)  # x1_max
Vin = np.arange(0, 3+interval, interval)  # x1_max


Vin_sweep = np.concatenate((Vin, np.flip(Vin)))

print("Num write/reads for 2 loops:", 2*len(Vin_sweep))



obj.ElectrodeState()

input("Press Enter to start sweeps... ")

sweep_Vin = []
sweep_Vout = []
sweep_Iout = []

All_Vin = []
All_Vout = []
All_Vadc = []
All_Iout = []

time_list = []
tref = time.time()

num_sweeps = 3
for sweep in range(num_sweeps):

    Vin = []
    Vout = []
    Iout = []
    for v in Vin_sweep:

        v = np.round(v,3)

        obj.SetVoltage(electrode=p, voltage=v)
        #time.sleep(2)
        # op = obj.ReadVoltage(OP, debug=0)  # ch0, pin3, op1

        Iop, Vop, Vadc = obj.ReadIV(OP, ret_type='both', nSamples=40)

        Vin.append(v)
        Vout.append(Vop)
        Iout.append(Iop)
        All_Vin.append(v)
        All_Vout.append(Vop)
        All_Vadc.append(Vadc)
        All_Iout.append(Iop)
        time_list.append(time.time()-tref)

        print("Vin=", v, " Vout=", Vop, ",  I=", Iop)
        #input("Press Enter to move to next input V")

    sweep_Vin.append(Vin)
    sweep_Vout.append(Vout)
    sweep_Iout.append(Iout)

obj.fin()



# save data
location = "%s/data.hdf5" % (save_dir)
with h5py.File(location, 'a') as hdf:
    G_sub = hdf.create_group("IO")

    for s in range(num_sweeps):
        G_subsub = G_sub.create_group("sweep_%d" % (s))
        G_subsub.create_dataset('Vin', data=sweep_Vin[s])
        G_subsub.create_dataset('Vout', data=sweep_Vout[s])
        G_subsub.create_dataset('Iout', data=sweep_Iout[s])




figI = plt.figure()
for s in range(num_sweeps):
    plt.plot(sweep_Vin[s], sweep_Iout[s], label=('sweep %d' % (s)))
plt.legend()
plt.xlabel('Vin')
plt.ylabel('Iout')
plt.title('Triangle wave sweep')
fig_path = "%s/FIG_Iout.png" % (save_dir)
figI.savefig(fig_path, dpi=300)
plt.close(figI)


figV = plt.figure()
for s in range(num_sweeps):
    plt.plot(sweep_Vin[s], sweep_Vout[s], label=('sweep %d' % (s)))
plt.legend()
plt.xlabel('Vin')
plt.ylabel('Vout')
plt.title('Triangle wave sweep')
fig_path = "%s/FIG_Vout.png" % (save_dir)
figV.savefig(fig_path, dpi=300)
plt.close(figV)


figV2 = plt.figure()
plt.plot(All_Vout)
plt.xlabel('Instance')
plt.ylabel('Vout')
plt.title('Triangle wave sweep')
fig_path = "%s/FIG_Vout_continuous.png" % (save_dir)
figV2.savefig(fig_path, dpi=300)
plt.close(figV2)


figV3 = plt.figure()
plt.plot(time_list, All_Vout)
plt.xlabel('Time')
plt.ylabel('Vout')
plt.title('Electrode voltage for a Triangle wave sweep')
fig_path = "%s/FIG_Vout_vs_time.png" % (save_dir)
figV3.savefig(fig_path, dpi=300)

figVadc = plt.figure()
plt.plot(time_list, All_Vadc)
plt.xlabel('Time')
plt.ylabel('Vout')
plt.title('Vadc output for a Triangle wave sweep')
fig_path = "%s/FIG_Vadc_vs_time.png" % (save_dir)
figVadc.savefig(fig_path, dpi=300)



plt.show()
plt.close('all')



# fin
