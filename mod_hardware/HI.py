#!/usr/bin/python3
import RPi.GPIO as GPIO # using RPi.GPIO
import spidev
import ctypes
import time
import os
import matplotlib.pyplot as plt
import numpy as np
from mod_hardware.mcpADC import mcp3204
###
# DPI tutorial: https://learn.sparkfun.com/tutorials/raspberry-pi-spi-and-i2c-tutorial/all
###




""" This is the Hardware Interface for the EiM PCB
For use with Microchips: MCP3204 and MCP4822

Note:
- Assigning both channels after a sincle cip select doesn't work.
- Chip select must be released and reactivated between blocks

"""


class Dac_bits(ctypes.LittleEndianStructure):
    """Class to define the DAC command register bitfields.
    See Microchip mcp4822 datasheet for more information
    """
    _fields_ = [
                   ("data", ctypes.c_uint16, 12),  # Bits 0:11
                   ("shutdown", ctypes.c_uint16, 1),  # Bit 12
                   ("gain", ctypes.c_uint16, 1),  # Bit 13
                   ("reserved1", ctypes.c_uint16, 1),  # Bit 14
                   ("channel", ctypes.c_uint16, 1)  # Bit 15
               ]

    # GA field value lookup. <gainFactor>:<bitfield val>
    __ga_field__ = {1:1, 2:0}
    def gain_to_field_val(self, gainFactor):
        """Returns bitfield value based on desired gain"""
        return self.__ga_field__[gainFactor]


class Dac_register(ctypes.Union):
    """Union to represent the DAC's command register
    See Microchip mcp4822 datasheet for more information
    """
    _fields_ = [
                   ("bits", Dac_bits),
                   ("bytes", ctypes.c_uint8 * 2),
                   ("reg", ctypes.c_uint16)
               ]


class hi:

    # ADC - variables
    __adcrefvoltage = 4.97 # 4.87 # 4.9 # 5  # reference voltage for the ADC (& DAC) chip.
    adc_adjusted_ref = 4.97  # used for scaling function
    __dacrefvoltage = 0.994 #0.994

    # DAC scale 1V ref is actually: 0.986V

    # # ADC (MCP3204) - Define SPI bus and init
    # # Clock speed > 10kHz,
    # # f_clk = 20*f_sample
    # # t_sample ~ 1.5 clocks
    spiADC = spidev.SpiDev()
    spiADC.open(0, 0)  # using CE0!!!
    # spiADC.speed = 900000
    spiADC.max_speed_hz = (2000000)  # 1000000, 2000000


    # # DAC (MCP4822) - Define SPI bus and init
    spiDAC = spidev.SpiDev()
    spiDAC.open(0, 1)  # not using CE1!!!
    spiDAC.no_cs = True  # Set the "SPI_NO_CS" flag to disable use of the chip select
    spiDAC.max_speed_hz = (4000000)

    # Max DAC output voltage. Depends on gain factor
    # The following table is in the form <gain factor>:<max voltage>
    __dacMaxOutput__ = {
                            1:2.048,  # This is Vref
                            2:4.096  # 4.096 if Vdd is 5V, 3.3 for 3.3v
                       }

    def __init__(self, gainFactor=1, adc_speed=None):
        """Class Constructor
        gainFactor -- Set the DAC's gain factor. The value should
           be 1 or 2.  Gain factor is used to determine output voltage
           from the formula: Vout = G * Vref * D/4096
           Where G is gain factor, Vref (for this chip) is 2.048 and
           D is the 12-bit digital value
        """

        # # Check gain factor
        if (gainFactor != 1) and (gainFactor != 2):
            print ("Warning: Invalid gain factor, must be 1 or 2. \n >> Set to 1 <<")
            self.gain = 1
        elif gainFactor == 2:
            print ("Warning: HIv2 DAC Gain Factor must equal 1. \n >> Set to 1 <<")
            self.gain = 1
        else:
            self.gain = gainFactor
            self.maxDacVoltage = self.__dacMaxOutput__[self.gain]

        # # Set ADC spi clock speed
        if adc_speed is not None:
            if adc_speed <= 2000000 and adc_speed >= 50000:
                self.spiADC.max_speed_hz = adc_speed
            else:
                raise ValueError("ADC speed is outside of allowed values (50000<Fclk<2000000)")

        #print("inside hit:", self.__adcrefvoltage)
        
        # # Assign chip enable (CE) GPIO pins
        self.CE = {}

        # # define DAC CE pins
        self.CE['DAC1'] = 27
        self.CE['DAC2'] = 17
        self.CE['DAC3'] = 18
        self.CE['DAC4'] = 23
        self.CE['DAC5'] = 24
        self.CE['DAC6'] = 25
        self.CE['DAC7'] = 26
        self.CE['DAC8'] = 19

        # # define ADC CE pins
        # self.CE['ADC1'] = 'CE0'

        # # define MUX control pins
        self.MUX = {}
        self.MUX['IN1'] = 22 # 12
        self.MUX['IN2'] = 5 # 16
        self.MUX['IN3'] = 6 # 20
        self.MUX['IN4'] = 13 # 21

        # # Assign current states to MUX pins
        self.MUX_Value = {}
        self.MUX_Value['IN1'] = 0
        self.MUX_Value['IN2'] = 0
        self.MUX_Value['IN3'] = 0
        self.MUX_Value['IN4'] = 0

        # # Set up GPIO board reference scheme
        GPIO.setmode(GPIO.BCM)

        # # Set up chip enable (CE) pins
        for chip in self.CE:
            GPIO.setup(self.CE[chip], GPIO.OUT) # set a port/pin as an output

        # # Set up MUX control pins
        for channel in self.MUX:
            GPIO.setup(self.MUX[channel], GPIO.OUT) # set a port/pin as an output


        # # Produce MCP3204 object
        self.mcp_adc = mcp3204(self.spiADC, self.CE, vref=self.__adcrefvoltage)

        # # Set all chip enable (CE) pins high
        for chip in self.CE:
            self.set_pin(self.CE[chip], 1)  # prevent further change by deactivating

        # # Set all MUX switches low
        for a_mux in self.MUX:
            self.set_pin(self.MUX[a_mux], 1)
            time.sleep(0.0001)
            self.set_pin(self.MUX[a_mux], 0)

        # # Set all electodes to 0V (i.e., DACs to 1v) (also done on exit)
        for chip in self.CE:
            if chip[0] == 'D':  # only set DACs
                self.set_dac(chip, 1, 1)
                self.set_dac(chip, 2, 1)

        return

    #

    def read_adc(self, chip='ADC1', channel=0, mode=0, return_raw=0):
        """
        Read a voltage value from one of the 4 channels.
        """

        raw = self.mcp_adc.Read(chip=chip, channel=channel, diff=mode)
        voltage = (self.__adcrefvoltage/4096)*raw

        if return_raw == 0:
            return voltage
        elif return_raw == 1:
            return voltage, raw
        else:
            raise ValueError("Return Raw argumnet must be 0 or 1.")

    #

    def read_adc_raw(self, chip='ADC1', channel=0, mode=0):
        """
        Read the raw binary voltage value from one of 4 channels.
        """

        # # Check if it is an activated chip and a ADC
        if chip not in self.CE:
            print("Invalid chip selected")
            return
        elif chip[0] != 'A':
            print("Chip must be an ADC")
            return

        voltage_raw = self.mcp_adc.Read(chip=chip, channel=channel, diff=mode)

        return voltage_raw

    #

    def read_adc_Average(self, chip='ADC1', channel=0, nAverage=30, bDebug=0, bDebug_graph=0, mode=0):
        """
        Read a series/burst of ADC values, average and return.
        """

        v_list = []
        tic = time.time()

        # # Burst reading (only requires 1 CE toggle)
        raw_list, t_list = self.mcp_adc.Read_burst(channel=channel, n=nAverage, diff=mode, tref=tic)

        # # Format Returned voltages
        for raw in raw_list:
            v_list.append((self.__adcrefvoltage/4096)*raw)
        fMean = np.mean(v_list)
        fstd = np.std(v_list)
        rawMean = np.mean(raw_list)
        rawStd = np.std(raw_list)

        toc = time.time()

        if bDebug:
            sample_rate = len(raw_list)/t_list[-1]
            print('nAverage = %d, mean value = %.3f, total run time = %f, sample rate ~ %f' % (nAverage, fMean, toc-tic, sample_rate))

        if bDebug_graph == 1:
            fig_debug = plt.figure()
            sample_rate = len(raw_list)/t_list[-1]
            plt.plot(t_list, v_list)
            plt.title('nAverage = %d, mean value = %.3f, std= %f \n total run time = %f, sample rate ~ %f' % (nAverage, fMean, fstd, toc-tic, sample_rate))
            if not os.path.exists('Results/Debug'):
                os.makedirs('Results/Debug')
            fig_debug.savefig('Results/Debug/read_adc_Average.png', dpi=300)
            # plt.show()
            plt.close(fig_debug)

        return fMean, fstd, rawMean, rawStd

    #

    def set_dac(self, chip, channel, voltage):
        """
        Set a voltage (within allowed range),
            - for the selected channel on the DAC
            - voltage can be between 0 and 2.047 volts
        """

        # print("Voltage to be set on DAC:", voltage, ", Chip:", chip, ", channel:", channel)

        if ((channel > 2) or (channel < 1)):
            print ("DAC channel needs to be 1 (A) or 2 (B)")

        if (voltage >= 0.0) and (voltage < self.maxDacVoltage):
            rawval = (voltage / 2.048) * 4096 / self.gain
            self.set_dac_raw(chip, channel, int(rawval))
        else:
            print("Invalid DAC Vout value %f. Must be between 0 and %f (non-inclusive) " % (voltage, self.maxDacVoltage))

        return

    #

    def set_dac_raw(self, chip, channel, value):
        """
        Set the raw value from the selected channel on the DAC.
            - Channel = 1 (A) or 2 (B).
            - Value between 0 and 4095.
        (translates the numerical set voltage and applies it to the chip buffer)
        """

        if (value < 0.0) or (value > 4095):
            print('Error (HI.py): raw DAC input was too large')
            return

        # # Check if it is an activated chip and a DAC
        if chip not in self.CE:
            print("Invalid chip selected")
            return
        elif chip[0] != 'D':
            print("Chip must be a DAC")
            return

        reg = Dac_register()

        # # Configurable fields
        reg.bits.data = value
        reg.bits.channel = channel - 1
        reg.bits.gain = reg.bits.gain_to_field_val(self.gain)

        # # Fixed fields:
        reg.bits.shutdown = 1  # Active low, i.e on => 1

        # # fetch pin number for selected chip
        # pin = self.CE[chip]

        # # Write to device
        self.set_pin(self.CE[chip], 0)  # chips are active low
        self.spiDAC.xfer2( [ reg.bytes[1], reg.bytes[0] ])
        self.set_pin(self.CE[chip], 1)  # prevent further change by deactivating

        return

    #

    def set_mux(self, mux, value):
        """
        Set the a mux ('INx') switch to:
            - 0 (output from electrode)
            - 1 (input to electrode)

        Note: return a value of 1 if there is an error, 0 for a success
        """

        # # check if a valid mux was selected
        if mux not in self.MUX:
            print("Invalid MUX selected")
            return 1

        # # check valid channel is selected
        if value != 1 and value != 0:
            print("Invalid channel selected: must be 0 (output from electrode) or 1 (input to electrode)")
            return 1

        # # check to see if value is already in that state
        if self.MUX_Value[mux] == value:
            # print("Switch is already at set state i.e., MUX %s at %d" % (mux, value))
            return 1

        # # check to see at least 1 mux is has output selected
        if value == 1:  # if trying to set a switch to electrode input
            num_mux_on = 0
            for a_mux in self.MUX_Value:
                if a_mux in self.MUX:  #  catch initiated MUX pins only
                    state = self.MUX_Value[a_mux]
                    if state == 1:
                        num_mux_on = num_mux_on + 1
            if num_mux_on >= len(self.MUX)-1:  # test to see if this is the final MUX on 0 (output selected)
                print("Error (set_mux): There must be at least one electrode output enabled")
                return 1

        # # fetch pin number for selected channel to change
        pin = self.MUX[mux]

        # # Write level to pin
        self.set_pin(pin, value)  # value == level
        self.MUX_Value[mux] = value

        print("Set mux %s to: %d" % (mux, value))

        return 0

    #

    def set_pin(self, pin, level):
        """
        Set a GPIO fin logic level
        """
        # only allow activated pins to be set
        if (pin in self.CE.values()) or (pin in self.MUX.values()):
            #print("pin", pin, "is going to", level)
            if level == 0 or level == 1:
                GPIO.output(pin, level)       # set port/pin value to 1/GPIO.HIGH/True
                # time.sleep(0.00002)  # does this execute properly (i.e add delay after change?? test)
                #print('post GPIO change')
            else:
                print("level must be 0 (LOW) or 1 (HIGH)")
        else:
            print('Invalid GPIO pin selected')
            return 1

        return 0

    #

    def fin(self):
        """
        Close program & tidy up.
        """

        # # set all electrodes to 0V (i.e., DACs to 1v)
        for chip in self.CE:
            if chip[0] == 'D':  # only set DACs
                self.set_dac(chip, 1, 1)
                self.set_dac(chip, 2, 1)

        # # Set all chip enable (CE) pins to 0v
        for chip in self.CE:
            self.set_pin(self.CE[chip], 0)  # prevent further change by deactivating

        # # Set MUX control pins to 0v
        for switch in self.MUX:
            self.set_pin(self.MUX[switch], 0)

        # # Close spi conns
        if self.spiADC is not None:
            self.spiADC.close
            self.spiADC = None
        if self.spiDAC is not None:
            self.spiDAC.close
            self.spiDAC = None

        # # Clean up GPIO
        GPIO.cleanup()

        # # Exit Message
        print("HI is now shut down via the R-Pi connection.")

        return

    #

    #

    @property
    def adcrefvoltage(self):
        return self.__adcrefvoltage

    @property
    def dacrefvoltage(self):
        return self.__dacrefvoltage

#

#

# fin
