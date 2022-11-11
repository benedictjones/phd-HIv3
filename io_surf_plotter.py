import numpy as np
import time
import h5py
import matplotlib.pyplot as plt
from tqdm import tqdm

from matplotlib.colors import LinearSegmentedColormap  # allows the creation of a custom cmap
import matplotlib
import cmocean  # extra perceptually uniform cmaps  https://matplotlib.org/cmocean/

# from scipy.stats import linregress

from _norm_color import MidpointNormalize

import os
from datetime import datetime


def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


# #################################

res = {}
res['IO'] = {}


#

# # Loop and average
dir = 'Results/2022_08_23/LDN_surf'


with h5py.File("%s/data.hdf5" % (dir), 'r') as hdf:

    OPs = np.array(hdf.get('OPs'))
    Vcs = np.array(hdf.get('Vcs'))
    res['extent'] = np.array(hdf.get('extent'))



    for op in OPs:
        G = hdf.get('/IO/OP%d/' % (op))

        res['IO']['OP%d' % (op)] = {}
        res['IO']['OP%d' % (op)]['Vo'] = np.array(G.get('Vo'))
        res['IO']['OP%d' % (op)]['Bo'] = np.array(G.get('Bo'))

    res['lims_Vo'] = np.array(hdf.get('lims_Vo'))
    res['lims_Bo'] = np.array(hdf.get('lims_Bo'))

    G_res = hdf.get('/residuals/')
    res['residuals'] = {}
    for key in G_res.keys():
        res['residuals'][key] = np.array(G_res.get(key))

# exit()


op_max = 0
op_min = 0
b_max = 0
b_min = 0
for o, OP in enumerate(OPs):


    if np.max(res['residuals']['op_%d__v' % (OP)]) >= op_max:
        op_max = np.max(res['residuals']['op_%d__v' % (OP)])

    if np.min(res['residuals']['op_%d__v' % (OP)]) <= op_min:
        op_min = np.min(res['residuals']['op_%d__v' % (OP)])

    if np.max(res['residuals']['op_%d__bit' % (OP)]) >= b_max:
        b_max = np.max(res['residuals']['op_%d__bit' % (OP)])

    if np.min(res['residuals']['op_%d__bit' % (OP)]) <= b_min:
        b_min = np.min(res['residuals']['op_%d__bit' % (OP)])

#



#

matplotlib .rcParams['axes.linewidth'] = 1  # box edge
#matplotlib .rcParams['mathtext.fontset'] = 'Arial'  # 'cm'
matplotlib.rc('pdf', fonttype=42)  # embeds the font, so can import to inkscape
matplotlib .rcParams["legend.labelspacing"] = 0.25

matplotlib .rcParams['lines.linewidth'] = 0.85
matplotlib .rcParams['lines.markersize'] = 3.5
matplotlib .rcParams['lines.markeredgewidth'] = 0.5

#

minn = res['lims_Vo'][0]
maxx = res['lims_Vo'][1]
minn, maxx = -5,5
print("Vlims:", minn, maxx)

basic_cols = ['#009cff', '#6d55ff', '#ffffff', '#ff6d55','#ff8800']  # pastal orange/red/white/purle/blue
my_cmap = LinearSegmentedColormap.from_list('mycmap', basic_cols)
my_cmap = cmocean.cm.balance

w = int(len(Vcs))*2.5
h = int(len(OPs))*3
fig, axs = plt.subplots(int(len(OPs)), int(len(Vcs)), sharex='col', sharey='row', squeeze=False, figsize=(w,h))
for o, op in enumerate(OPs):

    for c, Vc in enumerate(Vcs):

        im = axs[o,c].imshow(res['IO']['OP%d' % (op)]['Vo'][:,:,c], origin="lower", extent=res['extent'],
                            #vmin=res['lims_Vo'][0], vmax=res['lims_Vo'][1],
                            norm=MidpointNormalize(midpoint=0, vmin=minn, vmax=maxx),
                            cmap=my_cmap)

        axs[o,c].set_title("OP %d, Vc=%.3f" % (op, Vc))

        if c == 0:
            axs[o,c].set_ylabel("Vin2")

        if o == (len(OPs)-1):
            axs[o,c].set_xlabel("Vin1")


# fig.subplots_adjust(bottom=0.2)
cbar = fig.colorbar(im, ax=axs[:,:] , shrink=0.8, location='bottom', extend='both') # ,orientation='horizontal' , extend = 'both'
cbar.set_label('Vo', fontsize=10)

fig_path = "%s/FIG_surf_OP.png" % (dir)
fig.savefig(fig_path, dpi=200)

fig_path = "%s/FIG_surf_OP.pdf" % (dir)
fig.savefig(fig_path)

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

    axs[o].set_yscale('log')

    if OP == OPs[-1]:
        axs[o].set_xlabel('Bit Residuals')



fig_path = "%s/FIG_residuals_bit.png" % (dir)
fig.savefig(fig_path, dpi=150)
plt.close(fig)


fig, axs = plt.subplots(len(OPs))
for o, OP in enumerate(OPs):
    dat = res['residuals']['op_%d__v' % (OP)]

    deets = 'mean=%f, std=%f' % (np.mean(dat), np.std(dat))

    bwidth = 0.002
    axs[o].hist(dat, bins=np.arange(min(dat), max(dat)+bwidth, bwidth), label=deets)
    # axs[o].set_title("OP %d" % (OP))
    axs[o].set_xlim(op_min,op_max)
    axs[o].set_ylabel("OP %d Count" % (OP))
    if OP == OPs[-1]:
        axs[o].set_xlabel('Vop Residuals')

    axs[o].set_yscale('log')
    axs[o].legend()
    # axs[o].set_title(deets)

fig_path = "%s/FIG_residuals_v_log.png" % (dir)
fig.savefig(fig_path, dpi=150)
plt.close(fig)


fig, axs = plt.subplots(len(OPs))
for o, OP in enumerate(OPs):
    dat = res['residuals']['op_%d__v' % (OP)]

    deets = 'mean=%f, std=%f' % (np.mean(dat), np.std(dat))

    bwidth = 0.002
    axs[o].hist(dat, bins=np.arange(min(dat), max(dat)+bwidth, bwidth), label=deets)
    # axs[o].set_title("OP %d" % (OP))

    #xs[o].set_xlim(op_min,op_max)
    axs[o].set_xlim(-0.2,0.2)

    axs[o].set_ylabel("OP %d Count" % (OP))
    if OP == OPs[-1]:
        axs[o].set_xlabel('Vop Residuals')

    #axs[o].set_yscale('log')
    #axs[o].legend()
    # axs[o].set_title(deets)

fig_path = "%s/FIG_residuals_v.png" % (dir)
fig.savefig(fig_path, dpi=150)
plt.close(fig)

#

#

# fin
