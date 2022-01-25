import numpy as np
import time
import h5py
import matplotlib.pyplot as plt

from scipy.stats import linregress

import os
from datetime import datetime


"""
# Example enter to exit loop
for i in range(5):
    print("if pin %d is connected to OP %d" % (i, i))
    answer = (input("Enter anything to continue (press e to exit): " ))
    if str(answer) == 'e':
        break
    else:
        pass
    print(i)

exit()
"""

#

"""  # Pin 1-op4
    input_v_offset_grad = 0.03542 # 0.03579
    input_v_offset_constant = 0.339 # 0.335 # 0.33 # 0.35  # voltage offset at input electrodes (used when scaling)

"""

# # Location
location = "mod_software/calibrate_data.hdf5"

# # save data
if os.path.isfile(location) == False:
    with h5py.File(location, 'a') as hdf:
        G_sub = hdf.create_group("Input_Offset")
        G_sub.create_dataset('Constant', data=np.zeros(16))
        G_sub.create_dataset('Gradient', data=np.zeros(16))

        G_sub2 = hdf.create_group("Output_Offset")
        G_sub2.create_dataset('Constant', data=np.zeros(4))
        G_sub2.create_dataset('Gradient', data=np.zeros(4))

exit()

with h5py.File(location, 'r') as hdf:
    InOffset_C_bias = np.array(hdf.get('/Input_Offset/Constant'))
    InOffset_G_bias = np.array(hdf.get('/Input_Offset/Gradient'))
print(InOffset_C_bias)
print(InOffset_G_bias)

exit()
# # Make a Change
with h5py.File(location, 'r+') as hdf:
    InOffset_C_bias = hdf.get('/Input_Offset/Constant')
    InOffset_C_bias[:] = np.ones(16)
    InOffset_C_bias[1] = 20
    InOffset_G_bias = hdf.get('/Input_Offset/Gradient')
    InOffset_G_bias[:] = np.ones(16)

    OutOffset_C_bias = hdf.get('/Output_Offset/Constant')
    OutOffset_C_bias[:] = np.ones(4)
    OutOffset_G_bias = hdf.get('/Output_Offset/Gradient')
    OutOffset_G_bias[:] = np.ones(4)

with h5py.File(location, 'r') as hdf:
    InOffset_C_bias = np.array(hdf.get('/Input_Offset/Constant'))
    InOffset_G_bias = np.array(hdf.get('/Input_Offset/Gradient'))
print(InOffset_C_bias)
print(InOffset_G_bias)

exit()

#

# ###########################

#

#Reading the MCP3008 analog input channels and printing them.
import time

#import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

# Software SPI configuration:
# CLK  = 18
# MISO = 23
# MOSI = 24
# CS   = 25
# mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} |'.format(*range(4)))
print('-' * 28)
# Main program loop.
while True:
    # Read all the ADC channel values in a list.
    values = [0]*4
    for i in range(4):
        # The read_adc function will get the value of the specified channel (0-3).
        values[i] = mcp.read_adc(i)
    # Print the ADC values.
    print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} |'.format(*values))
    # Pause for half a second.
    time.sleep(0.5)

#

# ######################

#

#!/usr/bin/env python

import time
import pigpio

LOOPS=10000
CHANNELS=4

def read_MCP3008(adc, channel):
   count, data = pi.spi_xfer(adc, [1, (8+channel)<<4, 0])
   value = ((data[1] << 8) | data[2]) & 0x3FF
   return value

pi = pigpio.pi()

if not pi.connected:
   exit()

adc = pi.spi_open(0, 1e6) # CE0

start = time.time()

for i in range(LOOPS):
   for c in range(CHANNELS):
      v = read_MCP3008(adc, c)

finish = time.time()

reads = LOOPS * CHANNELS
runtime = finish - start

print("did {} reads in {:.1f} seconds ({}sps)".
   format(reads, runtime, int(reads/runtime)))

pi.spi_close(adc)

pi.stop()










# fin
