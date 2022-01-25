import RPi.GPIO as GPIO # using RPi.GPIO
import time
import copy


class mcp3204():

    def __init__(self, spiADC, CE_dict, vref):
        self.spiADC = spiADC
        self.channelCount = 4
        self.vref = vref
        self.resolution = 12
        self.MSB_MASK = 2**(self.resolution-8) - 1
        self.CE = CE_dict

        return

    #

    def Read(self, chip, bus_data, channel=0, diff=0):
        """
        Perform a single read after setting the chip select.
        """

        # Format data
        bus_data = self._FormatData_(channel, diff)
        CE = self.CE[chip]

        # read data
        v_raw = self._read_(CE, bus_data)

        return v_raw

    #

    def Read_burst(self, chip, channel=0, n=1, diff=0, tref='na'):
        """
        Perform a burst (i.e., loop) of readings.
        Note: the CE must be toggled for each read.
        """

        # # Create time list and ref
        time_list = []
        if tref == 'na':
            tref = time.time()

        # # Format Data Once to be used each loop
        bus_data = self._FormatData_(channel, diff)

        # # create returnable list of readings
        v_raw_list = []
        CE = self.CE[chip]

        # # read data in a loop
        # Include format data in the loop
        for i in range(n):
            #bus_data = self._FormatData_(channel, diff)  # must include in the loop
            cbus_data = copy.deepcopy(bus_data)
            v_raw_list.append(self._read_(CE, cbus_data))  # copy.deepcopy(bus_data)
            time_list.append(time.time()-tref)
            # time.sleep(0.0001)

        return v_raw_list, time_list

    #

    def _read_(self, CE, bus_data):
        """
        Perform a single read using the passed in Bus Data.
        """

        GPIO.output(CE, 0)  # Set CE low
        v_raw = self._read_raw_(bus_data)
        GPIO.output(CE, 1)  # Set CE high

        return v_raw

    #

    def _read_raw_(self, bus_data):
        """
        Sends the configured data to execute a read on a channel.
        Returns the read voltage.
        """

        # Read data
        r = self.spiADC.xfer(bus_data)  # or us r = self.xfer2(data) ?

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

    def mcp_set_pin(self, pin, level):
        """
        Set a GPIO logic levels for chip select.
        """

        GPIO.output(pin, level)  # set port/pin value to 1/GPIO.HIGH/True

        # time.sleep(0.000002)  # does this execute properly (i.e add delay after change?? test)

        return
