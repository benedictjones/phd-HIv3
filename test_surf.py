import numpy as np
import time
import h5py
import matplotlib.pyplot as plt
from tqdm import tqdm

from matplotlib.colors import LinearSegmentedColormap  # allows the creation of a custom cmap

from scipy.stats import linregress

import os
from datetime import datetime

from _norm_color import MidpointNormalize

# # Target Dir
save_dir = 'Results/2022_05_17/16_59_07_PKs_surf_s9_'
save_dir = 'Results/2022_05_17/17_00_00_PKs_surf_s9_'
save_dir = 'Results/2022_05_17/17_00_29_PKs_surf_s9_'


# # load data
res = {}

location = "%s/data.hdf5" % (save_dir)
with h5py.File(location, 'r') as hdf:

    # Vcs = list(hdf.keys())

    IO = hdf.get('IO')

    Vcs = []
    for k, v in IO.items():

        print(k)
        if k == 'extent':
            res['extent'] = np.array(v)
        else:
            res[k] = {}
            Vc = float(k)
            Vcs.append(Vc)

            res['%.3f' % Vc]['Vo'] = np.array(IO.get('%s/Vo' % (k)))
            res['%.3f' % Vc]['Bo'] = np.array(IO.get('%s/Bo' % (k)))
            res['%.3f' % Vc]['Io'] = np.array(IO.get('%s/Io' % (k)))
            res['num_op'] = np.shape(res['%.3f' % Vc]['Vo'])[-1]
    Vo2 = np.array(hdf.get('IO/0.000/Vo'))
#

print(np.shape(res['%.3f' % Vc]['Vo']))
print(np.shape(Vo2))
# exit()

basic_cols = ['#009cff', '#6d55ff', '#ffffff', '#ff6d55','#ff8800']  # pastal orange/red/white/purle/blue
my_cmap = LinearSegmentedColormap.from_list('mycmap', basic_cols)

# fig, ax = plt.subplots(nrows=1, ncols=len(Vcs),  sharey='row')

for op in range(res['num_op']):
    fig = plt.figure()
    for c, Vc in enumerate(Vcs):

        min = np.min(res['%.3f' % Vc]['Vo'])
        max = np.max(res['%.3f' % Vc]['Vo'])

        # ax = fig.add_subplot(1, len(Vcs), c+1)
        fig, ax = plt.subplots(int(1), int(len(Vcs)), sharex='col', sharey='row', squeeze=False)


        im = ax[0,c].imshow(res['%.3f' % Vc]['Vo'][:,:,op], origin="lower", extent=res['extent'],
                          # vmin=min, vmax=max,
                          #clim=(min, max),
                          norm=MidpointNormalize(midpoint=0.,vmin=min, vmax=max),
                          cmap=my_cmap)

        ax[0,c].set_title("Vc=%.3f" % (Vc))

        if c == 0:
            ax[0,c].set_ylabel("Vin2")
        ax[0,c].set_xlabel("Vin1")

    cbar = fig.colorbar(im, orientation='horizontal')
    cbar.set_label('Vo', fontsize=10)



    fig_path = "%s/FIG_surf_OP%d.png" % (save_dir, op)
    fig.savefig(fig_path, dpi=250)
    plt.close(fig)


# plt.show()
# plt.close('all')

#

#

#

# fin
