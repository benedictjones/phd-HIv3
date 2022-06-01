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
Rsh = 470 # 100000, 470
obj = si(Rshunt=Rsh, ADCspeed=ADCfclk)  # 14000 , 47000, , electrode11='in'

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
OP =  4 # 4
numS = 10 # 30

test_label = 'IO_sweep__p%s_Op%d' % (p,OP)
#test_label = 'IO_sweep__p%s_Op%d__8_2Meg_%dFadc' % (p,OP, ADCfclk)
# test_label = 'PKs_s9__p2_p15'
test_label = 'PKs_mnt__p%s_Op%d' % (p,OP)

#test_label = 'NWs_mnt_clip__p%s_Op%d' % (p,OP)
#test_label = 'NWs_'
#test_label = 'CustomDRN__Op%d' % (OP)

test_label = 'Custom_LDRN'

save_dir = "Results/%s/%s_%s" % (d_string, t_string, test_label)
os.makedirs(save_dir)

# ################################


interval = 0.025 # 0.05, 0.025 #  DAC-QE~0.0005, ADC-QE~0.002V
x1_max = 9 # 3.5, 3
Vin = np.arange(-x1_max, x1_max+interval, interval)  # neg to pos

#Vin = np.arange(0, x1_max+interval, interval)  # zero to pos
#Vin = np.arange(-x1_max, 0+interval, interval)  # neg to zero

#Vin = np.arange(0, 3+interval, interval)  # x1_max

direction = 'random' # forward, backward, random

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

sweep_Vin = []
sweep_Vout = []
sweep_Iout = []
sweep_dV = []
sweep_Vdac = []
sweep_Vadc = []
sweep_bit_values = []

All_Vin = []
All_Vout = []
All_dV = []
All_Vadc = []
All_Iout = []
All_bit_values = []

time_list = []
tref = time.time()

pbar = tqdm(total=num_sweeps*len(Vin_sweep))
for sweep in range(num_sweeps):

    Vins = []
    Vouts = []
    dVs = []
    Iouts = []
    Vdacs = []
    Vadcs = []
    ADC_bit_values = []
    for v in Vin_sweep:

        v = np.round(v,3)

        Vdac = obj.SetVoltage(electrode=p, voltage=v)
        #time.sleep(2)
        # op = obj.ReadVoltage(OP, debug=0)  # ch0, pin3, op1

        Iop, Vop, Vadc, adc_bit_value = obj.ReadIV(OP, ret_type=1, nSamples=numS)  # more samples gives a better/smoother average

        Vins.append(v)
        Vouts.append(Vop)
        dVs.append(v-Vop)
        Iouts.append(Iop)
        Vdacs.append(Vdac)
        Vadcs.append(Vadc)
        ADC_bit_values.append(adc_bit_value)
        All_Vin.append(v)
        All_Vout.append(Vop)
        All_dV.append(v-Vop)
        All_Vadc.append(Vadc)
        All_Iout.append(Iop)
        All_bit_values.append(adc_bit_value)
        time_list.append(time.time()-tref)

        # print("Vin=", v, " Vout=", Vop, ",  I=", Iop)
        #input("Press Enter to move to next input V")

        pbar.set_description("%d/%d | Vi=%.3f, Vo=%.3f, Io=%s" % (sweep+1, num_sweeps, v, Vop, str(Iop)))
        pbar.update(1)

    sweep_Vin.append(Vins)
    sweep_Vout.append(Vouts)
    sweep_dV.append(dVs)
    sweep_Iout.append(Iouts)
    sweep_Vdac.append(Vdacs)
    sweep_Vadc.append(Vadcs)
    sweep_bit_values.append(ADC_bit_values)

pbar.close()
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
        G_subsub.create_dataset('Vdac', data=sweep_Vdac[s])
        G_subsub.create_dataset('Vadc', data=sweep_Vadc[s])
        G_subsub.create_dataset('ADC_bit_values', data=sweep_bit_values[s])

#

markers = ['x', '*', 'o', '^', 'd']

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

    if direction == 'random':
        plt.scatter(sweep_dV[s], sweep_Iout[s], marker=markers[s], label=('sweep %d, R=%.1f' % (s, Rm)))
    else:
        plt.plot(sweep_dV[s], sweep_Iout[s],label=('sweep %d, R=%.1f' % (s, Rm)))
    

plt.legend()
plt.xlabel('dV')
plt.ylabel('Iout')
plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
plt.title('Voltage drop against current\nMean R=%.2f' % (np.mean(R_slopes)))
fig_path = "%s/FIG_Vd_vs_Iout.png" % (save_dir)
figI.savefig(fig_path, dpi=200)
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
figI.savefig(fig_path, dpi=200)
plt.close(figI)
"""
#



figV = plt.figure()
for s in range(num_sweeps):
    if direction == 'random':
        plt.scatter(sweep_Vin[s], sweep_Vout[s], marker=markers[s],  label=('sweep %d' % (s)))
    else:
        plt.plot(sweep_Vin[s], sweep_Vout[s], label=('sweep %d' % (s)))
plt.legend()
plt.xlabel('Vin')
plt.ylabel('Vout')
plt.title('Voltage Sweep\n(Interval= %s, Sample Size=%d, type=%s)' % (str(interval), numS, direction))
fig_path = "%s/FIG_Vin_vs_Vout.png" % (save_dir)
figV.savefig(fig_path, dpi=200)
# plt.close(figV)

#

figV = plt.figure()
for s in range(num_sweeps):
    if direction == 'random':
        plt.scatter(sweep_Vin[s], sweep_bit_values[s], marker=markers[s], label=('sweep %d' % (s)))
    else:
        plt.plot(sweep_Vin[s], sweep_bit_values[s], label=('sweep %d' % (s)))
plt.legend()
plt.grid()
plt.xlabel('Vin')
plt.ylabel('ADC Bits value')
plt.title('Voltage Sweep (Interval= %s)' % (str(interval)))
fig_path = "%s/FIG_Vin_vs_ADCbits.png" % (save_dir)
figV.savefig(fig_path, dpi=200)
plt.close(figV)

#

if direction != 'random':
    figV2 = plt.figure()
    plt.plot(All_Vout)
    plt.xlabel('Instance')
    plt.ylabel('Vout')
    plt.title('Triangle wave sweep')
    fig_path = "%s/FIG_Vout_continuous.png" % (save_dir)
    figV2.savefig(fig_path, dpi=200)
    plt.close(figV2)

#

if direction != 'random':
    figV3 = plt.figure()
    plt.plot(time_list, All_Vout)
    plt.xlabel('Time')
    plt.ylabel('Vout')
    plt.title('Electrode voltage for a Triangle wave sweep')
    fig_path = "%s/FIG_TRI_Vout_vs_time.png" % (save_dir)
    figV3.savefig(fig_path, dpi=200)
    plt.close(figV3)
#


figV4 = plt.figure()
plt.plot(All_bit_values)
plt.xlabel('Instance')
plt.ylabel('ADC bit value')
plt.title('Electrode voltage for a Triangle wave sweep\nInstance set/read rate = %f' % (num_sweeps*len(Vin_sweep)/t_read))
fig_path = "%s/FIG_TRI_ADCbits.png" % (save_dir)
figV4.savefig(fig_path, dpi=200)
plt.close(figV4)

#

if direction != 'random':
    figVadc = plt.figure()
    plt.plot(time_list, All_Vadc)
    plt.xlabel('Time')
    plt.ylabel('Vadc')
    plt.title('Vadc output for a Triangle wave sweep')
    fig_path = "%s/FIG_TRI_Vadc_vs_time.png" % (save_dir)
    figVadc.savefig(fig_path, dpi=200)
    plt.close(figVadc)

#

#

fig = plt.figure()
for s in range(num_sweeps):
    if direction == 'random':
        plt.scatter(sweep_Vdac[s], sweep_Vadc[s], marker=markers[s], label=('sweep %d' % (s)))
    else:
        plt.plot(sweep_Vdac[s], sweep_Vadc[s], label=('sweep %d' % (s)))
plt.legend()
plt.xlabel('Vdac')
plt.ylabel('Vadc')
plt.title('Real hardware values')
fig_path = "%s/FIG_Vdac_vs_Vadc.png" % (save_dir)
fig.savefig(fig_path, dpi=200)
plt.close(fig)

fig = plt.figure()
for s in range(num_sweeps):
    if direction == 'random':
        plt.scatter(sweep_Vin[s], sweep_Vdac[s], marker=markers[s], label=('sweep %d' % (s)))
    else:
        plt.plot(sweep_Vin[s], sweep_Vdac[s], label=('sweep %d' % (s)))
plt.legend()
plt.xlabel('Vin')
plt.ylabel('Vdac')
plt.title('Set voltage is translated to a hardware DAC voltage')
fig_path = "%s/FIG_Vin_vs_Vdac.png" % (save_dir)
fig.savefig(fig_path, dpi=200)
plt.close(fig)

fig = plt.figure()
for s in range(num_sweeps):
    if direction == 'random':
        plt.scatter(sweep_Vadc[s], sweep_Vout[s], marker=markers[s], label=('sweep %d' % (s)))
    else:
        plt.plot(sweep_Vadc[s], sweep_Vout[s], label=('sweep %d' % (s)))
plt.legend()
plt.xlabel('Vadc')
plt.ylabel('Vout')
plt.title('Read ADC value is translated back to the output')
fig_path = "%s/FIG_Vout_vs_Vadc.png" % (save_dir)
fig.savefig(fig_path, dpi=200)
plt.close(fig)
#

plt.show()
plt.close('all')



# fin
