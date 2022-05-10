from mod_software.SI import si
import numpy as np
import time
import h5py
import matplotlib.pyplot as plt
from tqdm import tqdm

from scipy.stats import linregress

import os
from datetime import datetime


ADCfclk = 1000000 # 2000000
obj = si(Rshunt=100000, ADCspeed=ADCfclk)  # 14000 , 47000

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



p_a1 = 1
p_a2 = 2
p_c1 = 3
OPs = [4]

test_label = 'IO_surf__p%s_Op%d' % (p,OP)
test_label = 'IO_surf__p%s_Op%d__8_2Meg_%dFadc' % (p,OP, ADCfclk)
# test_label = 'PKs_surf_s9__p2_p15'
#test_label = 'PKs_surf_mnt__p%s_Op%d' % (p,OP)

save_dir = "Results/%s/%s_%s" % (d_string, t_string, test_label)
os.makedirs(save_dir)

# ################################


interval = 0.01 # 0.05 #  DAC-QE~0.0005, ADC-QE~0.002V
x1_max = 3  # 3.5, 3
Vin = np.arange(-x1_max, x1_max+interval, interval)  # x1_max
#Vin = np.arange(0, 3+interval, interval)  # x1_max
#Vin_sweep = np.random.uniform(-x1_max, x1_max, 800)

Vin1s = np.arange(-x1_max, x1_max+interval, interval)
Vin2s = np.arange(-x1_max, x1_max+interval, interval)
Vo = np.zeros((len(Vin1s), len(Vin2s), len(OPs)))
Io = np.zeros((len(Vin1s), len(Vin2s), len(OPs)))

Vc = 0

num_sets = len(Vin1s)*len(Vin2s)*len(OPs)
print("Num write/reads:", num_sets)

obj.ElectrodeState()

input("Press Enter to start sweeps... ")

tref = time.time()
pbar = tqdm(total=num_sets)
for i, Vin1 in enumerate(Vin1s):
    for j, Vin2 in enumerate(Vin2s):

        # # Set voltages
        Vdac1 = obj.SetVoltage(electrode=p_a1, voltage=np.round(Vin1,3))
        Vdac2 = obj.SetVoltage(electrode=p_a2, voltage=np.round(Vin2,3))
        Vdac3 = obj.SetVoltage(electrode=p_c1, voltage=np.round(Vc,3))

        # # Read Voltages
        for k, OP in enumerate(OPs):
            Iop, Vop, Vadc, adc_bit_value = obj.ReadIV(OP, ret_type=1, nSamples=30)
            Vo[j, i, k] = Vop
            Io[j, i, k] = Iop

            pbar.set_description("V1 %d/ V2 %d | OP %d:  Vo=%.3f, Io=%s" % (Vin1, Vin2, OP, Vop, str(Iop)))
            pbar.update(1)

#

pbar.close()
t_read = time.time()-tref
obj.fin()
print("Time to do all readings = %f" % (t_read))
print("Instance set/read rate = %f" % (num_sets/t_read))


















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
    plt.plot(sweep_Vin[s], sweep_Vout[s], label=('sweep %d' % (s)))
plt.legend()
plt.xlabel('Vin')
plt.ylabel('Vout')
plt.title('Voltage Sweep (Interval= %s)' % (str(interval)))
fig_path = "%s/FIG_Vin_vs_Vout.png" % (save_dir)
figV.savefig(fig_path, dpi=200)
plt.close(figV)

#

figV = plt.figure()
for s in range(num_sweeps):
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

figV2 = plt.figure()
plt.plot(All_Vout)
plt.xlabel('Instance')
plt.ylabel('Vout')
plt.title('Triangle wave sweep')
fig_path = "%s/FIG_Vout_continuous.png" % (save_dir)
figV2.savefig(fig_path, dpi=200)
# plt.close(figV2)

#

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
