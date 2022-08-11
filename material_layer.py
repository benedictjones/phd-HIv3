# # Top Matter
import numpy as np
import time
import os
import h5py
import sys
import yaml
from random import random

from material import Material


class PiM_processor(object):

    def __init__(self, prm):
        """
        Initialise object
        """
        self.prm = prm

        # # Generate Physical Material Object
        self.mobj = Material(prm)

        return

    #

    #

    #

    def solve_layer(self, lVdata, lVc):
        """
        Takes a layers input voltages, re-organises and solves using
        material model.
        """
        # tic = time.time()

        if np.max(lVdata) > self.prm['spice']['Vmax']:
            raise ValueError("A data input voltage (%.2f) exceeds the max allowed input voltage (%.2f)" % (np.max(lVdata), self.prm['spice']['Vmax']))
        elif np.min(lVdata) < self.prm['spice']['Vmin']:
            raise ValueError("A data input voltage (%.2f) exceeds the min allowed input voltage (%.2f)" % (np.min(lVdata), self.prm['spice']['Vmin']))


        # # Check passed in voltage to calc
        if np.shape(lVdata)[1] != self.prm['network']['num_input']*self.prm['network']['hiddenSize']:
            raise ValueError("Data voltage array with %d columns cannot be passed into material layer expecting %d cols." % (len(lVdata), self.prm['network']['num_input']*self.prm['network']['hiddenSize']))

        # # Check passed in config voltages
        if len(lVc) != self.prm['network']['num_config']*self.prm['network']['hiddenSize']:
            raise ValueError("Config voltage array of %d cannot be passed into material with %d voltage application nodes." % (len(lVc), self.prm['network']['num_config']*self.prm['network']['hiddenSize']))

        #

        # # Calc Output From each material in layer
        Vout = []
        for m in range(self.prm['network']['hiddenSize']):

            # Break up Vin
            idxs = m*self.prm['network']['num_input']
            idxe = m*self.prm['network']['num_input']+self.prm['network']['num_input']
            Vdata = lVdata[:, idxs:idxe]

            idxs = m*self.prm['network']['num_config']
            idxe = m*self.prm['network']['num_config']+self.prm['network']['num_config']
            Vc = lVc[idxs:idxe]
            Vc = np.full((len(Vdata), len(Vc)), Vc)

            Vin = np.concatenate((Vdata, Vc), axis=1)
            Vo = self.mobj.solve_material(Vin)

            Vout.append(Vo)

        # # Produce a single layer output array
        Vout = np.concatenate(np.array(Vout), axis=1)

        #

        # # Check output voltage dimensions
        if np.shape(Vout)[1] != self.prm['network']['num_output']*self.prm['network']['hiddenSize']:
            raise ValueError("Output voltage array with %d columns should have %d cols." % (np.shape(Vout)[1], (self.prm['network']['num_output']*self.prm['network']['hiddenSize'])))


        #print("Time to solve layer = ", time.time()-tic)
        #exit()

        return Vout

    #

    def fin(self):
        """
        Delete material layer object by shutting down SI and HI+GPIO connections
        """
        self.mobj.fin()
        del self.mobj
        print("Material object delected, re-initialise Material Layer to start up again.")

        return

    #

    #

    #

    #

    #

    #

    #


#

#

# fin
