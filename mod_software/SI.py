from mod_hardware.HI import hi
import time
import numpy as np
import h5py

""" Software Interface for the EiM PCB
For use with the Hardware Interface (HI).
This Software Interface (SI) allows useful functionsto be carried out
e.g
        - Setting voltage at an electrode
        - reading a voltage from an output electrode
        - reading all output voltages
        - etc.
"""


class si:

    # Initialise Object Variables
    RC_delay = 0  # a delay added to allow the voltages to settle

    # # Use offset which can be found by calibrating
    # # When Calibrating, perdorm Calibrate_DACs, then Calibrate_ADCs
    input_v_offset = 0  # y = mx + c voltage offset at input electrodes (used when scaling)
    output_v_offset = 0  # y = mx + c voltage offset at output electrodes (used when scaling)

    # Set defualt of which DAC or ADC is associated to which electrode
    electode_device = {
                        1:'DAC1',
                        2:'DAC1',
                        3:'ADC1',
                        4:'DAC2',
                        5:'DAC2',
                        6:'DAC3',
                        7:'DAC3',
                        8:'ADC1',
                        9:'DAC4',
                        10:'DAC4',
                        11:'ADC1',
                        12:'DAC5',
                        13:'DAC5',
                        14:'DAC6',
                        15:'DAC6',
                        16:'ADC1',
                        }

    # Set defualt channel: DAC is 1(A) or 2(B), ADC is 1 to 4 (if all outputs are in use)
    electode_channel = {
                        1:1,
                        2:2,
                        3:0,  # ADC ch0, op1, pin3
                        4:1,
                        5:2,
                        6:1,
                        7:2,
                        8:1,   # ADC ch1, op2, pin8
                        9:1,
                        10:2,
                        11:3,  # ADC ch3, op3, pin11
                        12:1,
                        13:2,
                        14:1,
                        15:2,
                        16:2,  # ADC ch2, op4, pin16
                        }


    # Initialise the object
    def __init__(self, electrode3='out', electrode8='out', electrode11='out', electrode16='out',
                 Rshunt='none', ADCspeed=None):
        """
        Inititalise the Software Interface (SI) object.
        """

        # # Load in Input (DAC) Offset Arrays from previous Calibration
        if self.input_v_offset == 1:
            with h5py.File("mod_software/calibrate_data.hdf5", 'r') as hdf:
                self.InOffset_C_bias = np.array(hdf.get('/Input_Offset/Constant'))
                self.InOffset_G_bias = np.array(hdf.get('/Input_Offset/Gradient'))

        # # Load in Output (ADC) Offset Arrays from previous Calibration
        if self.output_v_offset == 1:
            with h5py.File("mod_software/calibrate_data.hdf5", 'r') as hdf:
                self.OutOffset_C_bias = np.array(hdf.get('/Output_Offset/Constant'))
                self.OutOffset_G_bias = np.array(hdf.get('/Output_Offset/Gradient'))

        # # Create hardware interface (HI) object
        self.hi = hi(adc_speed=ADCspeed)
        print("\n>>>", self.hi.adcrefvoltage)

        # # Set max voltage
        self.maxDacVoltage = self.hi.maxDacVoltage

        # # Set values to self
        self.Rshunt = Rshunt  # value in ohms or 'na'=='none'

        # # set the 4 optional i/o electrodes (minmum one output)
        self.SetElectrodes(electrode3, electrode8, electrode11, electrode16)

        # # Set all Electrodes to 0V
        for elec in self.electode_device:
            if 'DAC' in self.electode_device[elec]:
                self.SetVoltage(electrode=elec, voltage=0)

        return

    #

    def SetVoltage(self, electrode=1, voltage=0):
        """
        Set a voltage on an electrode (this is scaled by the hardware design).

        Note: The hardware scales the DAC voltage [0,2]V to [-10,10]V.
        """

        # # Check that the selected electode is a DAC (i.e., an input)
        if self.electode_device[electrode][0] != 'D':
            print('Selected electrode is not configured as a DAC')
            return 1

        # # Scale voltage according to the hardware gain
        V_dac = self.Scale_InputV_to_DAC(voltage, electrode)
        V_adc_ideal = self.Scale_ADC_to_OutputV(voltage, inverse=1)

        # print("Set Electrode to %fV, DAC to %fV, ideal 1:1 ADC reading:%fV" % (voltage, V_dac, V_adc_ideal))

        # # Error check and set new voltage
        if V_dac > 2:
            print('Warning: Electrode voltage %fV (i.e., DAC Voltage %fV) is not possible' % (voltage, V_dac))
            print('  > DAC Voltage cannot be greater than 2V')
            print('  > Post HI Scaling Voltage cannot be greater than %f' % (self.Scale_InputV_to_DAC(2, inverse=1)))
            return 1
        elif V_dac < 0:
            print('Warning: Electrode voltage %fV (i.e., DAC Voltage %fV) is not possible' % (voltage, V_dac))
            print('  > DAC Voltage cannot be less than 0V')
            print('  > Post HI Scaling Voltage cannot be less than %fV' % (self.Scale_InputV_to_DAC(0, inverse=1)))
            return 1
        else:
            self.hi.set_dac(self.electode_device[electrode], self.electode_channel[electrode], V_dac)

        # time.sleep(0.05)

        return V_dac

    #

    def SetAllVoltages(self, voltage_list):
        """
        Set all Voltages using a passed in list.
        """

        # # Fetch a list of all the electrodes assigned to DACs (i.e., inputs)
        DAC_electrode_list = []
        for k, v in self.electode_device.items():
            if v[0] == 'D':
                DAC_electrode_list.append(k)

        # # Error Check and appy voltages
        if len(voltage_list) != len(DAC_electrode_list):
            print("Error (SI.py): Input voltage list not match the number of DAC (input) electrodes")
            return 1
        else:
            loc = 0
            for electrode in DAC_electrode_list:
                self.hi.set_dac(self.electode_device[electrode], self.electode_channel[electrode], voltage_list[loc])
                loc = loc + 1

        # # Pause operation to allow system to settle
        # time.sleep(self.RC_delay)

        return 0

    #

    def ReadIV(self, location, loc_scheme='output', nSamples=20, ret_type=0):
        """
        Read a voltage from an electrode.

        loc_scheme is used to set the type of output selection:
            loc_scheme = 'output' (1 to 4)
            loc_scheme = 'channel' (0 to 3)
            loc_scheme = 'electrode' output electrode location (3, 8, 11, 16)

        Three return types:
            - "0"   returns: Iop, Vop
            - "1"   returns: Iop, Vop, Vadc, raw_bit_value
        """

        vop, v_adc, bit_adc = self.ReadVoltage(location, loc_scheme, nSamples, ret_type=1)  # ch0, pin3, op1

        # # Calc current from shunt resistance
        if self.Rshunt == 'none':
            I = 0
        else:
            I = vop/self.Rshunt

        # Return
        if ret_type == 0:
            return np.round(I,11), vop

        elif ret_type == 1:
            return np.round(I,11), vop, v_adc, bit_adc


    #

    def ReadVoltage(self, location, loc_scheme='output', nSamples=20, debug=0, ret_type=0):
        """
        Read a voltage from an electrode.

        loc_scheme is used to set the type of output selection:
            loc_scheme = 'output' (1 to 4)
            loc_scheme = 'channel' (0 to 3)
            loc_scheme = 'electrode' output electrode location (3, 8, 11, 16)

        Three return types:
            - "raw" returns: Vadc, Vadc_std
            - "0"   returns: Vop
            - "1"   returns: Vop, Vadc, raw_bit_value

        Note: The hardware scales the electode voltages from [-10,10]V to
        [0,5]V so the ADC can read them.
        """

        # # Fetch list of active ADCs (i.e., outputs)
        # # and there electrodes + channels
        ADC_electrode_list = []
        ADC_channel_list = []
        for k, v in self.electode_device.items():
            if v[0] == 'A':
                ADC_electrode_list.append(k)
                ADC_channel_list.append(self.electode_channel[k])

        # # Format selected input location to correct channel indexing
        if loc_scheme == 'output':
            if location == 1:
                sel_ch = 0
            elif location == 2:
                sel_ch = 1
            elif location == 3:
                sel_ch = 3
            elif location == 4:
                sel_ch = 2

            if sel_ch in ADC_channel_list:
                the_channel = sel_ch
            else:
                print("Error (SI.py): Selected output not available to read from.")
                return

        elif loc_scheme == 'channel':
            if location in ADC_channel_list:
                the_channel = location
            else:
                print("Error (SI.py): Selected ADC channel not available to read from.")
                return

        elif loc_scheme == 'electrode':
            if location in ADC_electrode_list:
                the_channel = self.electode_channel[location]
            else:
                print("Error (SI.py): Selected output electrode not available to read from.")
                return

        else:
            print("Error (SI.py): Invalide output reference scheme. Use 'output' or 'electrode'.")
            return

        #

        # # Try to get a good reading with a low number of samples
        attempts = [1, 2, 3, 4]
        for attempt in attempts:

            success = 0

            # # Read Voltage using a "burst and average read"
            Vadc, Vadc_std, bit, bit_std = self.hi.read_adc_Average(chip='ADC1',
                                                                       channel=the_channel,
                                                                       nAverage=nSamples*attempt**2,
                                                                       bDebug=0, bDebug_graph=debug)

            """
            # # Run check on coefficient of variation (CV)
            CV = Vstd/Vadc
            print("\nVstd=%f, CV=%f" % (Vstd, CV))
            print("Vbit = %f" % ( (4 * (5/2**12)) ) )
            if CV < 1:
                success = success + 1
            else:
                print("attempt %d Read voltage failed coefficient of variation check..." % (attempt))
            #"""

            # # just break
            #break

            # OR

            #"""
            # # Run std vs quantisation noise check
            if bit_std <= 4:
                success = success + 1
            else:
                print("\nAttempt %d Read voltage failed std quantisation noise check... (bit std=%.4f)" % (attempt, bit_std))
                #print(" > std of ADC output = ", Vstd)
            #"""

            if success >= 1:
                #print(" > Pass! std of ADC output = ", Vstd)
                break
            elif attempt >= attempts[-1]:
                Vadc, Vadc_std, bit, bit_std = np.nan, np.nan, np.nan, np.nan
                #print("Warning: Read voltage failed its tests!")
                #self.fin()
                #return

        if ret_type == 'raw':
            return Vadc, Vadc_std

        # # Scale voltage by the hardware design
        vop = self.Scale_ADC_to_OutputV(Vadc, the_channel)

        if debug == 1:
            print("Output Electode voltage:", vop, ", Output ADC voltage:", Vadc)

        # print("Output Electode voltage:", vop, ", Output ADC voltage:", Vadc, " , chanel:", sel_ch)

        # Return
        if ret_type == 0:
            return np.round(vop,6)

        elif ret_type == 1:
            return np.round(vop,6), np.round(Vadc,6), np.round(bit,6)

    #

    def SetElectrodes(self, electrode3='na', electrode8='na', electrode11='na', electrode16='na'):
        """
        Sets the electrodes as input or output, by changing the MUX switching.
        Adjusts the reference device & channel dictionaries as required.
        """

        # # set electrode 3 (output 1)
        if electrode3 == 'out':
            error = self.hi.set_mux('IN1', 0)
            if error == 0:
                self.electode_device[3] = 'ADC1'
                self.electode_channel[3] = 0  # ADC ch0, op1
                self.hi.set_dac('DAC7', 1, 1)  # set electrode to 0v (DAC to 1v)
        elif electrode3 == 'in':
            error = self.hi.set_mux('IN1', 1)
            if error == 0:
                self.electode_device[3] = 'DAC7'
                self.electode_channel[3] = 1
                self.hi.set_dac('DAC7', 1, 1)  # set electrode to 0v (DAC to 1v)
        elif electrode3 != 'na':
            print("Invalide setting for electrode!\nMust be 'out' or 'in'.")

        # # set electrode 8 (output 2)
        if electrode8 == 'out':
            error = self.hi.set_mux('IN2', 0)
            if error == 0:
                self.electode_device[8] = 'ADC1'
                self.electode_channel[8] = 1  # ADC ch1, op2
                self.hi.set_dac('DAC7', 2, 1)  # set electrode to 0v (DAC to 1v)
        elif electrode8 == 'in':
            error = self.hi.set_mux('IN2', 1)
            if error == 0:
                self.electode_device[8] = 'DAC7'
                self.electode_channel[8] = 2
                self.hi.set_dac('DAC7', 2, 1)  # set electrode to 0v (DAC to 1v)
        elif electrode8 != 'na':
            print("Invalide setting for electrode!\nMust be 'out' or 'in'.")

        # # set electrode 11 (output 3)
        if electrode11 == 'out':
            error = self.hi.set_mux('IN4', 0)
            if error == 0:
                self.electode_device[11] = 'ADC1'
                self.electode_channel[11] = 3  # ADC ch3, op3
                self.hi.set_dac('DAC8', 2, 1)  # set electrode to 0v (DAC to 1v)
        elif electrode11 == 'in':
            error = self.hi.set_mux('IN4', 1)
            if error == 0:
                self.electode_device[11] = 'DAC8'
                self.electode_channel[11] = 2
                self.hi.set_dac('DAC8', 2, 1)  # set electrode to 0v (DAC to 1v)
        elif electrode11 != 'na':
            print("Invalide setting for electrode!\nMust be 'out' or 'in'.")

        # # set electrode 16 (output 4)
        if electrode16 == 'out':
            error = self.hi.set_mux('IN3', 0)
            if error == 0:
                self.electode_device[16] = 'ADC1'
                self.electode_channel[16] = 2  # ADC ch2, op4
                self.hi.set_dac('DAC8', 1, 1)  # set electrode to 0v (DAC to 1v)
        elif electrode16 == 'in':
            error = self.hi.set_mux('IN3', 1)
            if error == 0:
                self.electode_device[16] = 'DAC8'
                self.electode_channel[16] = 1
                self.hi.set_dac('DAC8', 1, 1)  # set electrode to 0v (DAC to 1v)
        elif electrode16 != 'na':
            print("Invalide setting for electrode!\nMust be 'out' or 'in'.")

        return

    #

    def ElectrodeState(self):
        """
        Prints the current state of the electrodes.
        """
        print("\nThe state of the electrodes:")
        for i in range(1, len(self.electode_device)+1):
            print("Electrode", i, ": ", self.electode_device[i], self.electode_channel[i])

        return

    #

    def Scale_InputV_to_DAC(self, V, electrode='ideal', inverse=0):
        """
        Taking the set electrode voltage, compute the required DAC voltage.

        Using a Differential Amplifier https://www.electronics-tutorials.ws/opamp/opamp_5.html
        so, the applied voltage:
            > Vo = (R2/R1)*(Vin-Vref),  where R2 = 100, R1 = 10, Vref is ideally 1V

        Note: The hardware scales the DAC voltage [0,2]V to [-10,10]V.
        The reference for this scaling is produced by a potential divider which
        which steps down the V_adc_ref by a factor of five.
        """

        # # Calaculate Offset from previous calibration
        if self.input_v_offset == 1 and electrode != 'ideal':
            offset = V*self.InOffset_G_bias[electrode-1] + self.InOffset_C_bias[electrode-1]
            # print(">>>", offset, ", m=", self.InOffset_G_bias[electrode-1], ", x=", self.InOffset_C_bias[electrode-1])
        else:
            offset = 0
            # print(">>>", offset)

        #

        # # Scale using offset
        Vref = self.hi.dacrefvoltage
        if inverse == 0:
            V_scaled = ((V + offset)/10) + Vref   # compute required DAC voltage for set electrode voltage
        elif inverse == 1:
            V_scaled = 10*(V - Vref) - offset  # compute electrode voltage for a set DAC voltage
        else:
            raise ValueError("Invalid inverse toggle.")

        return V_scaled

    #

    def Scale_ADC_to_OutputV(self, V, channel='ideal', inverse=0):
        """
        Taking the read ADC voltage, compute the electrode voltage.
        So, the output step:
            > Vadc = (2*Vref+Vin)/4,  where Vref is ideally 5V

        Note: The hardware scales the electode volrages from [-10,10]V to
        [0,V_adc_ref]V so the ADC can read them.
        """

        # # Calaculate Offset
        if self.output_v_offset == 1 and channel != 'ideal':
            offset = V*self.OutOffset_G_bias[channel] + self.OutOffset_C_bias[channel]
        else:
            offset = 0

        #

        # # Scale using offset
        Vref = self.hi.adc_adjusted_ref # self.hi.adcrefvoltage  # the system voltage ref (5V ideally)
        if inverse == 0:
            V_scaled = 4*V - 2*Vref + offset  # compute electrode voltage from a read ADC voltage
        elif inverse == 1:
            V_scaled = (V-offset)/4 + Vref/2  # compute the ADC voltage for an electrode voltage
        else:
            raise ValueError("Invalid inverse toggle.")

        return V_scaled

    #

    def fin(self):
        """
        Set all inputs to zero and shut down.
        """

        print("Shutting down hardware and R-Pi connection.")
        self.hi.fin()

        # # Delete HI object to prevent re-use or errors
        del self.hi
        print("HI object delected, re-initialise SI to start up again.")

        return

    #

# fin
