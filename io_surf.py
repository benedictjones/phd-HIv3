from mod_software.SI import si
import numpy as np
import time
import h5py
import matplotlib.pyplot as plt
from tqdm import tqdm

from matplotlib.colors import LinearSegmentedColormap  # allows the creation of a custom cmap

# from scipy.stats import linregress

from _norm_color import MidpointNormalize

import os
from datetime import datetime


ADCfclk = 2000000 # 2000000
Rsh = 470 # 100000, 470 # 14000 , 47000
obj = si(Rshunt=Rsh, ADCspeed=ADCfclk)

Rshunt = obj.Rshunt
num_sweeps = 1


# #################################
now = datetime.now()
real_d_string = now.strftime("%d_%m_%Y")
d_string = now.strftime("%Y_%m_%d")
print("Date:", real_d_string)
print("Date:", d_string)
t_string = now.strftime("%H_%M_%S")
print("Time Stamp:", t_string, "\n\n")



p_a1 = 1
p_a2 = 9
p_c1 = 2
OPs = [2,3,4]

#test_label = 'IO_surf__p%s_Op%d' % (p,OP)
#test_label = 'IO_surf__p%s_Op%d__8_2Meg_%dFadc' % (p,OP, ADCfclk)
test_label = 'PKs_surf_s9_'
#test_label = 'PKs_surf_mnt__p%s_Op%d' % (p,OP)

test_label = 'NWs_surf_'
test_label = 'Custom_LDRN_surf_'

save_dir = "Results/%s/%s_%s" % (d_string, t_string, test_label)
os.makedirs(save_dir)

# ################################


interval = 0.5 # 0.5 # 0.25 # 0.05 #  DAC-QE~0.0005, ADC-QE~0.002V
x1_max = 9  # 3.5, 3
Vin = np.arange(-x1_max, x1_max+interval, interval)  # x1_max
#Vin = np.arange(0, 3+interval, interval)  # x1_max
#Vin_sweep = np.random.uniform(-x1_max, x1_max, 800)

Vin1s = np.arange(-x1_max, x1_max+interval, interval)
Vin2s = np.arange(-x1_max, x1_max+interval, interval)
Vcs = [-8, -4, 0, 4, 8] # np.arange(-2, 2+1, 1)




num_sets = len(Vin1s)*len(Vin2s)*len(OPs)*len(Vcs)
print("Num write/reads:", num_sets)

obj.ElectrodeState()

input("Press Enter to start sweeps... ")

res = {}
res['extent'] = [np.min(Vin1s), np.max(Vin1s), np.min(Vin2s), np.max(Vin2s)]
res['OPs'] = OPs
for p, Vlist in enumerate([Vin1s, Vin2s, Vcs]):
    res['Vin%ds' % (p+1)] = Vlist
res['Vcs'] = Vcs
res['IO'] = {}

tref = time.time()
pbar = tqdm(total=num_sets)

Vo = np.zeros((len(Vin1s), len(Vin2s), len(Vcs), len(OPs)))
Io = np.zeros((len(Vin1s), len(Vin2s), len(Vcs), len(OPs)))
Bo = np.zeros((len(Vin1s), len(Vin2s), len(Vcs), len(OPs)))

res['residuals'] = {}
for o, OP in enumerate(OPs):
    res['residuals']['op_%d__bit' % (OP)] = []
    res['residuals']['op_%d__v' % (OP)] = []

for c, Vc in enumerate(Vcs):

    for i, Vin1 in enumerate(Vin1s):
        for j, Vin2 in enumerate(Vin2s):

            res['%.3f' % Vc] = {}

            # # Set voltages
            Vdac1 = obj.SetVoltage(electrode=p_a1, voltage=np.round(Vin1,3))
            Vdac2 = obj.SetVoltage(electrode=p_a2, voltage=np.round(Vin2,3))
            Vdac3 = obj.SetVoltage(electrode=p_c1, voltage=np.round(Vc,3))

            # # Read Voltages
            for o, OP in enumerate(OPs):
                # Iop, Vop, Vadc, adc_bit_value = obj.ReadIV(OP, ret_type=1, nSamples=1)  # fast
                Iop, Vop, vop_residuals, Bop, bit_residuals = obj.ReadVoltageResiduals(OP, nSamples=30)
                Vo[j, i, c, o] = Vop
                Io[j, i, c, o] = Iop
                Bo[j, i, c, o] = Bop

                res['residuals']['op_%d__bit' % (OP)].append(bit_residuals)
                res['residuals']['op_%d__v' % (OP)].append(vop_residuals) 

                pbar.set_description("Vc %.2f, V1 %.2f/ V2 %.2f | OP %d:  Vo=%.3f, Io=%s" % (Vc, Vin1, Vin2, OP, Vop, str(Iop)))
                pbar.update(1)
                # print(OP, Vop)
                #print("\n Vop %d R:" % (OP), Vop, vop_residuals)
                #print("Bop %d R:" % (OP), Bop, bit_residuals)
        #pbar.close()
        #exit()

pbar.close()
t_read = time.time()-tref
obj.fin()
print("Time to do all readings = %f" % (t_read))
print("Instance set/read rate = %f" % (num_sets/t_read))
# exit()

# # Add to save dict
for o, OP in enumerate(OPs):
    res['IO']['OP%d' % (OP)] = {}
    res['IO']['OP%d' % (OP)]['Vo'] = Vo[:, :, :, o]
    res['IO']['OP%d' % (OP)]['Io'] = Io[:, :, :, o]
    res['IO']['OP%d' % (OP)]['Bo'] = Bo[:, :, :, o]

res['lims_Vo'] = [np.min(Vo), np.max(Vo)]
res['lims_Io'] = [np.min(Io), np.max(Io)]
res['lims_Bo'] = [np.min(Bo), np.max(Bo)]


op_max = 0
op_min = 0
b_max = 0
b_min = 0
for o, OP in enumerate(OPs):
    res['residuals']['op_%d__bit' % (OP)] = np.concatenate(np.array(res['residuals']['op_%d__bit' % (OP)]))
    res['residuals']['op_%d__v' % (OP)] = np.concatenate(np.array(res['residuals']['op_%d__v' % (OP)]))
    #print("\n Vop %d resifuals:" % (OP), res['residuals']['op_%d__v' % (OP)])
    #print("  Max:", np.max(res['residuals']['op_%d__v' % (OP)]))
    #print("  Min:", np.min(res['residuals']['op_%d__v' % (OP)]))
    
    if np.max(res['residuals']['op_%d__v' % (OP)]) >= op_max:
        op_max = np.max(res['residuals']['op_%d__v' % (OP)])
    
    if np.min(res['residuals']['op_%d__v' % (OP)]) <= op_min:
        op_min = np.min(res['residuals']['op_%d__v' % (OP)])
    
    if np.max(res['residuals']['op_%d__bit' % (OP)]) >= b_max:
        b_max = np.max(res['residuals']['op_%d__bit' % (OP)])
    
    if np.min(res['residuals']['op_%d__bit' % (OP)]) <= b_min:
        b_min = np.min(res['residuals']['op_%d__bit' % (OP)])

#

# ######################################################
# # save data to file
# ######################################################
location = "%s/data.hdf5" % (save_dir)
with h5py.File(location, 'a') as hdf:

    for k, v in res.items():
        #print(k)

        if isinstance(v, dict):
            G_sub = hdf.create_group(k)
            for k2, v2 in res[k].items():
                #print(k, "layer 2:", k2)
                if isinstance(v2, dict):
                    G_sub2 = G_sub.create_group(k2)
                    for k3, v3 in res[k][k2].items():
                        #print("created:", k, " ,layer 2:", k2, " ,layer 3:", k3)
                        G_sub2.create_dataset(k3, data=v3)
                else:
                    #print("  > created L2:", k, k2)
                    G_sub.create_dataset(k2, data=v2)
        else:
            #print("  > created L1:", k)
            hdf.create_dataset(k, data=v)


#

# exit()

# ######################################################
# Plots
# ######################################################

#

minn = res['lims_Vo'][0]
maxx = res['lims_Vo'][1]
print("Vlims:", minn, maxx)

basic_cols = ['#009cff', '#6d55ff', '#ffffff', '#ff6d55','#ff8800']  # pastal orange/red/white/purle/blue
my_cmap = LinearSegmentedColormap.from_list('mycmap', basic_cols)


w = int(len(Vcs))*2.5
h = int(len(res['OPs']))*3
fig, axs = plt.subplots(int(len(res['OPs'])), int(len(Vcs)), sharex='col', sharey='row', squeeze=False, figsize=(w,h))
for o, op in enumerate(res['OPs']):

    for c, Vc in enumerate(Vcs):

        im = axs[o,c].imshow(res['IO']['OP%d' % (op)]['Vo'][:,:,c], origin="lower", extent=res['extent'],
                            #vmin=res['lims_Vo'][0], vmax=res['lims_Vo'][1],
                            norm=MidpointNormalize(midpoint=0, vmin=minn, vmax=maxx),
                            cmap=my_cmap)

        axs[o,c].set_title("OP %d, Vc=%.3f" % (op, Vc))

        if c == 0:
            axs[o,c].set_ylabel("Vin2")

        if o == (len(res['OPs'])-1):
            axs[o,c].set_xlabel("Vin1")


# fig.subplots_adjust(bottom=0.2)
cbar = fig.colorbar(im, ax=axs[:,:] , shrink=0.8, location='bottom') # ,orientation='horizontal'
cbar.set_label('Vo', fontsize=10)

fig_path = "%s/FIG_surf_OP.png" % (save_dir)
fig.savefig(fig_path, dpi=200)
plt.close(fig)

plt.show()
plt.close('all')

#


# # Histograms

fig, axs = plt.subplots(len(OPs))
for o, OP in enumerate(OPs):
    dat = res['residuals']['op_%d__bit' % (OP)]
    bwidth = 0.5
    axs[o].hist(dat, bins=np.arange(min(dat), max(dat)+bwidth, bwidth))
    axs[o].set_ylabel("OP %d Count" % (OP))
    
    axs[o].set_xlim(b_min,b_max)
    
    if OP == OPs[-1]:
        axs[o].set_xlabel('Bit Residuals')
        
        
        
fig_path = "%s/FIG_residuals_bit.png" % (save_dir)
fig.savefig(fig_path, dpi=150)
plt.close(fig)


fig, axs = plt.subplots(len(OPs))
for o, OP in enumerate(OPs):
    dat = res['residuals']['op_%d__v' % (OP)]
    bwidth = 0.002
    axs[o].hist(dat, bins=np.arange(min(dat), max(dat)+bwidth, bwidth))
    # axs[o].set_title("OP %d" % (OP))
    axs[o].set_xlim(op_min,op_max)
    axs[o].set_ylabel("OP %d Count" % (OP))
    if OP == OPs[-1]:
        axs[o].set_xlabel('Vop Residuals')
    
fig_path = "%s/FIG_residuals_v.png" % (save_dir)
fig.savefig(fig_path, dpi=150)
plt.close(fig)

#

#

# fin
