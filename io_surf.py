from mod_software.SI import si
import numpy as np
import time
import h5py
import matplotlib.pyplot as plt
from tqdm import tqdm

from matplotlib.colors import LinearSegmentedColormap  # allows the creation of a custom cmap

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
Vcs = [0, 1] # np.arange(-2, 2+1, 1)




num_sets = len(Vin1s)*len(Vin2s)*len(OPs)*len(Vcs)
print("Num write/reads:", num_sets)

obj.ElectrodeState()

input("Press Enter to start sweeps... ")

res = {}
res['extent'] = [np.min(Vin1s), np.max(Vin1s), np.min(Vin2s), np.max(Vin2s)]

tref = time.time()
pbar = tqdm(total=num_sets)

for Vc in Vcs:

    Vo = np.zeros((len(Vin1s), len(Vin2s), len(OPs)))
    Io = np.zeros((len(Vin1s), len(Vin2s), len(OPs)))
    Bo = np.zeros((len(Vin1s), len(Vin2s), len(OPs)))

    for i, Vin1 in enumerate(Vin1s):
        for j, Vin2 in enumerate(Vin2s):

            res['%.3f' % Vc] = {}

            # # Set voltages
            Vdac1 = obj.SetVoltage(electrode=p_a1, voltage=np.round(Vin1,3))
            Vdac2 = obj.SetVoltage(electrode=p_a2, voltage=np.round(Vin2,3))
            Vdac3 = obj.SetVoltage(electrode=p_c1, voltage=np.round(Vc,3))

            # # Read Voltages
            for k, OP in enumerate(OPs):
                Iop, Vop, Vadc, adc_bit_value = obj.ReadIV(OP, ret_type=1, nSamples=30)
                Vo[j, i, k] = Vop
                Io[j, i, k] = Iop
                Bo[j, i, k] = adc_bit_value

                pbar.set_description("Vc %.2f, V1 %.2f/ V2 %.2f | OP %d:  Vo=%.3f, Io=%s" % (Vc, Vin1, Vin2, OP, Vop, str(Iop)))
                pbar.update(1)

    res['%.3f' % Vc]['Vo'] = Vo
    res['%.3f' % Vc]['Io'] = Io
    res['%.3f' % Vc]['Bo'] = Bo

#

pbar.close()
t_read = time.time()-tref
obj.fin()
print("Time to do all readings = %f" % (t_read))
print("Instance set/read rate = %f" % (num_sets/t_read))


# save data
location = "%s/data.hdf5" % (save_dir)
with h5py.File(location, 'a') as hdf:
    G = hdf.create_group("IO")

    for k, v in res.items():

        if isinstance(v, dict):
            G_sub = G.create_group(k)
            for k2, v2 in res[k].items():
                G_sub.create_dataset(k2, data=v2)
        else:
            G.create_dataset(k, data=v)


#

#

basic_cols = ['#009cff', '#6d55ff', '#ffffff', '#ff6d55','#ff8800']  # pastal orange/red/white/purle/blue
my_cmap = LinearSegmentedColormap.from_list('mycmap', basic_cols)

fig, ax = plt.subplots(nrows=1, ncols=len(Vcs),  sharey='row')
for c, Vc in enumerate(Vcs):
    im = ax[c].imshow(res['%.3f' % Vc]['Vo'], origin="lower", extent=res['extent'],
                      # vmin=vMIN, vmax=vMAX,
                      cmap=my_cmap)

    ax[c].set_title("Vc=%.3f" % (Vc))

    if c == 0:
        ax[c].set_ylabel("Vin2")
    ax[c].set_xlabel("Vin1")

fig.colorbar(im, orientation='horizontal')


fig_path = "%s/FIG_surf.png" % (save_dir)
fig.savefig(fig_path, dpi=250)
plt.close(fig)


# plt.show()
# plt.close('all')

#

#

#

# fin
