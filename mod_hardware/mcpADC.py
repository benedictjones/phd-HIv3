import RPi.GPIO as GPIO # using RPi.GPIO
import time
import copy


class mcp3204():

    def __init__(self, spiADC, CE_dict, vref, pig=None):
        self.spiADC = spiADC
        self.channelCount = 4
        self.vref = vref
        self.resolution = 12
        self.MSB_MASK = 2**(self.resolution-8) - 1
        self.CE = CE_dict
        
        self.pig = pig
        
        return

    #

    def Read(self, channel=0, diff=0, timings=0):
        """
        Perform a single read.
        """
        tic = time.time()
        
        # Format data
        bus_data = self._FormatData_(channel, diff)
        #CE = self.CE[chip]   # CE use is depriciated now SPI CE (pin 24) in use

        # read data
        v_raw = self._read_(bus_data)

        if timings==0:
            return v_raw
        else:
            return v_raw, time.time()-tic
    #

    def Read_burst(self, channel=0, n=1, diff=0, tref='na'):
        """
        Perform a burst (i.e., loop) of readings.
        """

        # # Create time list and ref
        time_list = []
        if tref == 'na':
            tref = time.time()

        # # Format Data Once to be used each loop
        bus_data = self._FormatData_(channel, diff)

        # # create returnable list of readings
        v_raw_list = []
        #CE = self.CE[chip]  # CE use is depriciated now SPI CE (pin 24) is used

        # # read data in a loop
        # Include format data in the loop
        for i in range(n):
            cbus_data = self._FormatData_(channel, diff)  # must include in the loop
            #cbus_data = copy.deepcopy(bus_data)
            v_raw_list.append(self._read_(cbus_data))  # copy.deepcopy(bus_data)
            time_list.append(time.time()-tref)
            # time.sleep(0.0001)

        return v_raw_list, time_list

    #

    def _read_(self, bus_data, CE='CE0'):
        """
        Perform a single read using the passed in Bus Data.

        Note:
            - The CE must be toggled for each read.
            - Now this is done automatically via the SPI interface using SPI CE0 (GPIO 08)

        """

        if CE != 'CE0':
            raise ValueError("SPI interface handles the ADC chip enable!")


        #GPIO.output(CE, 0)  # Set CE low
        v_raw = self._read_raw_(bus_data)  # using dedicated SPI CE pin now
        #GPIO.output(CE, 1)  # Set CE high

        return v_raw

    #

    def _read_raw_(self, bus_data):
        """
        Sends the configured data to execute a read on a channel.
        Returns the read voltage.
        """

        # Read data
        if self.pig is None:
            r = self.spiADC.xfer(bus_data)  # or us r = self.xfer2(data) ?
            #print('spi:', r)

        else:
            c, r = self.pig.spi_xfer(self.spiADC, bus_data)
            #print('pigpio:', r)    
                

        return ((r[1] & self.MSB_MASK) << 8) | r[2]

    #

    def _FormatData_(self, channel, diff):
        d = [0x00, 0x00, 0x00]
        d[0] |= 1 << 2
        d[0] |= (not diff) << 1
        d[0] |= (channel >> 2) & 0x01
        d[1] |= ((channel >> 1) & 0x01) << 7
        d[1] |= ((channel >> 0) & 0x01) << 6
        return d

#

#

# fin
