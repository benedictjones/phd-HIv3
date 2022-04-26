from mod_software.SI import si
import numpy as np
import time
import h5py
import matplotlib.pyplot as plt

from scipy.stats import linregress

import os
from datetime import datetime



obj = si(Rshunt=56000)  # 14000

Rshunt = obj.Rshunt
num_sweeps = 2


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

test_label = 'IO_sweep__p%s_Op%d' % (p,OP)
#test_label = 'PKs_s9__p7_p16'
#test_label = 'PKs_mnt__p%s_Op%d' % (p,OP)

save_dir = "Results/%s/%s_%s" % (d_string, t_string, test_label)
os.makedirs(save_dir)

# ################################


interval = 0.025 # 0.05 # QE ~ 0.005V
x1_max = 3.5  # 3.5
Vin = np.arange(-x1_max, x1_max+interval, interval)  # x1_max
#Vin = np.arange(0, 3+interval, interval)  # x1_max


Vin_sweep = np.concatenate((Vin, np.flip(Vin)))
# Vin_sweep = np.random.uniform(-x1_max, x1_max, 800)

print("Num write/reads:", num_sweeps*len(Vin_sweep))



obj.ElectrodeState()

input("Press Enter to start sweeps... ")

sweep_Vin = []
sweep_Vout = []
sweep_Iout = []
sweep_dV = []

All_Vin = []
All_Vout = []
All_dV = []
All_Vadc = []
All_Iout = []

time_list = []
tref = time.time()


for sweep in range(num_sweeps):

    Vin = []
    Vout = []
    dV = []
    Iout = []
    for v in Vin_sweep:

        v = np.round(v,3)

        obj.SetVoltage(electrode=p, voltage=v)
        #time.sleep(2)
        # op = obj.ReadVoltage(OP, debug=0)  # ch0, pin3, op1

        Iop, Vop, Vadc = obj.ReadIV(OP, ret_type='both', nSamples=100)  # more samples gives a better/smoother average

        Vin.append(v)
        Vout.append(Vop)
        dV.append(v-Vop)
        Iout.append(Iop)
        All_Vin.append(v)
        All_Vout.append(Vop)
        All_dV.append(v-Vop)
        All_Vadc.append(Vadc)
        All_Iout.append(Iop)
        time_list.append(time.time()-tref)

        print("Vin=", v, " Vout=", Vop, ",  I=", Iop)
        #input("Press Enter to move to next input V")

    sweep_Vin.append(Vin)
    sweep_Vout.append(Vout)
    sweep_dV.append(dV)
    sweep_Iout.append(Iout)

t_read = time.time()-tref
obj.fin()
print("Time to do all readings = %f" % (t_read))
print("Instance set/read rate = %f" % (num_sweeps*len(Vin_sweep)/t_read))

# save data
location = "%s/data.hdf5" % (save_dir)
with h5py.File(location, 'a') as hdf:
    G_sub = hdf.create_group("IO")

    for s in range(num_sweeps):
        G_subsub = G_sub.create_group("sweep_%d" % (s))
        G_subsub.create_dataset('Vin', data=sweep_Vin[s])
        G_subsub.create_dataset('Vout', data=sweep_Vout[s])
        G_subsub.create_dataset('dV', data=sweep_dV[s])
        G_subsub.create_dataset('Iout', data=sweep_Iout[s])

#

figI = plt.figure()
R_slopes = []
for s in range(num_sweeps):
    
    if Rshunt == 'none':
        Rm = np.nan
    else:
        reg = linregress(x=sweep_dV[s], y=sweep_Iout[s])
        Rm = 1/reg.slope
        print("Sweep %d, Rmaterial ~ %.1f" % (s,Rm))
        R_slopes.append(Rm)
        
    plt.plot(sweep_dV[s], sweep_Iout[s], label=('sweep %d, R=%.1f' % (s, Rm)))
    
plt.legend()
plt.xlabel('dV')
plt.ylabel('Iout')
plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
plt.title('Voltage drop against current\nMean R=%.2f' % (np.mean(R_slopes)))
fig_path = "%s/FIG_Vd_Iout.png" % (save_dir)
figI.savefig(fig_path, dpi=300)
plt.close(figI)

#
"""
figI = plt.figure()
for s in range(num_sweeps):
    plt.plot(sweep_Vout[s], sweep_Iout[s], label=('sweep %d' % (s)))
plt.legend()
plt.xlabel('Vout')
plt.ylabel('Iout')
plt.title('Output Voltage against current')
plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
fig_path = "%s/FIG_Vout_Iout.png" % (save_dir)
figI.savefig(fig_path, dpi=300)
plt.close(figI)
"""
#

figV = plt.figure()
for s in range(num_sweeps):
    plt.plot(sweep_Vin[s], sweep_Vout[s], label=('sweep %d' % (s)))
plt.legend()
plt.xlabel('Vin')
plt.ylabel('Vout')
plt.title('Voltage Sweep')
fig_path = "%s/FIG_Vout.png" % (save_dir)
figV.savefig(fig_path, dpi=300)
plt.close(figV)

#

figV2 = plt.figure()
plt.plot(All_Vout)
plt.xlabel('Instance')
plt.ylabel('Vout')
plt.title('Triangle wave sweep')
fig_path = "%s/FIG_Vout_continuous.png" % (save_dir)
figV2.savefig(fig_path, dpi=300)
plt.close(figV2)

#

figV3 = plt.figure()
plt.plot(time_list, All_Vout)
plt.xlabel('Time')
plt.ylabel('Vout')
plt.title('Electrode voltage for a Triangle wave sweep')
fig_path = "%s/FIG_TRI_Vout_vs_time.png" % (save_dir)
figV3.savefig(fig_path, dpi=300)
plt.close(figV3)
#

figV4 = plt.figure()
plt.plot(All_Vout)

plt.xlabel('Instance')
plt.ylabel('Vout')
plt.title('Electrode voltage for a Triangle wave sweep\nInstance set/read rate = %f' % (num_sweeps*len(Vin_sweep)/t_read))
fig_path = "%s/FIG_TRI_Vout.png" % (save_dir)
figV4.savefig(fig_path, dpi=300)

#

figVadc = plt.figure()
plt.plot(time_list, All_Vadc)
plt.xlabel('Time')
plt.ylabel('Vadc')
plt.title('Vadc output for a Triangle wave sweep')
fig_path = "%s/FIG_TRI_Vadc_vs_time.png" % (save_dir)
figVadc.savefig(fig_path, dpi=300)
plt.close(figVadc)
#

plt.show()
plt.close('all')



# fin
