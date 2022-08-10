# # Top Matter
import numpy as np
import time

from collections import namedtuple


from mod_material.spice.GenerateRN import generate_random_netork
from mod_material.spice.Network_Run import Run_circuit_model
from mod_methods.FetchPerm import IndexPerm



class Material(object):

    def __init__(self, prm, syst, l=0, n=0):
        """
        Initialise object
        """
        self.prm = {'network': prm['network'], 'spice': prm['spice']}

        self.syst = syst
        self.l = l
        self.n = n

        self.mstring = None

        self.gen_system(syst)

        return

    #

    #

    def gen_system(self, syst):
        """
        Generate Material
        """

        # # Genertate a material (if it is not Neuromorphic!!)
        self.mstring, self.description = generate_random_netork(self.prm, syst, self.l, self.n)

        return

    #

    def solve_material(self, Vin):
        """
        Checks input voltage, then computes output voltage using PySpice model.
        """

        # # Check passed in voltage to calc
        if np.shape(Vin)[1] != (self.prm['network']['num_input'] + self.prm['network']['num_config']):
            raise ValueError("Voltage array length %d cannot be passed into material with %d voltage application nodes." % (len(Vin), (self.prm['network']['num_input'] + self.prm['network']['num_config'])))

        #

        # # Calculate the voltage output of input training data
        for attempt in [1,2,3]:
            try:
                # l,m = layer-index, material-in-layer-index
                Vout = Run_circuit_model(Vin, self.mstring, self.prm)
                break
            except Exception as e:
                time.sleep(np.random.rand()/10)
                print("Attempt", attempt, "failed... \n Re trying to calculate output voltages.")
                if attempt == 3:
                    print("Error (solve_material, Run_circuit_model): Failed to calculate output voltages\n\n")
                    raise ValueError(e)
                else:
                    pass

        #

        # # Check output voltage
        if np.shape(Vout)[1] != self.prm['network']['num_output']:
            raise ValueError("Voltage array length %d cannot be passed into material with %d voltage application nodes." % (len(Vin), (self.prm['network']['num_input'] + self.prm['network']['num_config'])))

        # print("  Time to solve material = ", time.time()-tic)

        return Vout

    #

#

#

#

#

#

#

# fin
