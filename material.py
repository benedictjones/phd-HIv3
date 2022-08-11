# # Top Matter
import numpy as np
import time
from mod_software.SI import si


class Material(object):

    def __init__(self, prm, syst, l=0, n=0):
        """
        Initialise object
        """
        self.prm = {'network': prm['network'], 'spice': prm['spice']}

        self.syst = syst
        self.l = l
        self.n = n

        # # Run some checks
        if len(self.prm['spice']['in_pins']) != (self.prm['network']['num_input']+self.prm['network']['num_config']):
            raise ValueError("Number of input voltage pins %d does not match number input network nodes %d" % (len(self.prm['spice']['in_pins']), (self.prm['network']['num_input']+self.prm['network']['num_config'])))
        elif len(self.prm['spice']['out_pins']) != self.prm['network']['num_output']:
            raise ValueError("Number of output voltage pins %d does not match number output network nodes %d" % (len(self.prm['spice']['out_pins']), self.prm['network']['num_output']))


        self.SI = si(Rshunt=self.prm['spice']['op_shunt_R'])

        return

    #

    #

    #

    def solve_material(self, Vin):
        """
        Checks input voltage, then computes output voltage using PySpice model.
        """
        # tic = time.time()

        # # Check passed in voltage to calc
        if np.shape(Vin)[1] != (self.prm['network']['num_input'] + self.prm['network']['num_config']):
            raise ValueError("Voltage array length %d cannot be passed into material with %d voltage application nodes." % (len(Vin), (self.prm['network']['num_input'] + self.prm['network']['num_config'])))

        # # Calc Outputs
        Vout = self.calc(Vin)

        # # Check output voltage
        if np.shape(Vout)[1] != self.prm['network']['num_output']:
            raise ValueError("Voltage array length %d cannot be passed into material with %d voltage application nodes." % (len(Vin), (self.prm['network']['num_input'] + self.prm['network']['num_config'])))

        # print("  Time to solve material = ", time.time()-tic)

        return Vout
    #

    def calc(self, Vin_all):
        """
        Perfom loop to set and read all the voltages on the physical system
        """

        Vop_all = np.zeros((len(Vin_all), len(self.prm['spice']['out_pins'])))
        for row, Vins in enumerate(Vin_all):

            # # Set Voltages
            for i in range(len(self.prm['spice']['in_pins'])):
                self.SI.SetVoltage(electrode=self.prm['spice']['in_pins'][i], voltage=Vins[i])

            # # Read Outputs
            for col, OP in enumerate(self.prm['spice']['out_pins']):
                Iop, Vop, Vadc, adc_bit_value = self.SI.ReadIV(OP, ret_type=1, nSamples=self.prm['spice']['num_samples'])
                Vop_all[row, col] = Vop

        return Vop_all
    #

    def fin(self):
        """
        Delete material object by shutting down SI and HI+GPIO connections
        """
        self.SI.fin()
        del self.SI
        print("SI object delected, re-initialise Material to start up again.")

        return
#

#

#

#

#

#

# fin
