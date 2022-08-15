from mod_software.SI import si
import numpy as np
import time
import h5py
import matplotlib.pyplot as plt
from tqdm import tqdm

from scipy.stats import linregress

import os
from datetime import datetime


'''
Testing speed of system.

THere are different ways of using GPIO:
- https://codeandlife.com/2012/07/03/benchmarking-raspberry-pi-gpio-speed/
- Can use GPIO package
- Can use others like WiringPi2, or pigpio, Gpiozero

Check Package version:
- pip3 show ____

Ways to speed up:
- use latest RPi.GPIO 0.7.1!!! (https://sourceforge.net/p/raspberry-gpio-python/wiki/install/)
- try pigpio (https://abyz.me.uk/rpi/pigpio/python.html)

'''






ADCfclk = 2000000 # 2000000
obj = si(Rshunt=470, ADCspeed=ADCfclk)  # 14000 , 47000, , electrode11='in'


in_pins = [1,9,2]
out_pins = [2,3,4]
numS = 30 # 30

rng = np.random.default_rng(0)
num_v = 100
s = (num_v, len(in_pins))
Vins = rng.uniform(-5,5, size=s)

t_dac_total = 0
t_dac_spi = 0
t_dac_gpio = 0

t_adc_total = 0
t_adc_sample = 0
t_adc_per_sample = []

t_instance = []

tic_start = time.time()

for v in Vins:

    tic = time.time()

    # # Set Voltages
    for in, inPin in enumerate(in_pins):
        V_dac, t_spi, t_gpio, t_total = obj.SI.SetVoltage(electrode=inPin, voltage=v[in], timings=1)
        t_dac_total += t_total
        t_dac_spi += t_spi
        t_dac_gpio += t_gpio

    # # Read Outputs
    for col, OP in enumerate(out_pins):
        Vop, t_total_all, t_av_sample, t_burst = obj.SI.ReadVoltageFast(OP, ret_type=0, nSamples=numS, timings=1)
        t_adc_total += t_total_all
        t_adc_sample += t_burst
        t_adc_per_sample.append(t_av_sample)

    t_instance.append(time.time() - tic)




obj.fin()


total = time.time()-tic_start
print("\n>> Total Time = %f <<" % (total))


print("\nTotal DAC Time = %f (%f p of total) <<" % (t_dac_total, t_dac_total/total))
print("  - DAC SPI  Time = %f (%f p of total) <<" % (t_dac_spi, t_dac_spi/total))
print("  - DAC GPIO Time = %f (%f p of total) <<" % (t_dac_gpio, t_dac_gpio/total))

print("\nTotal ADC Time = %f (%f p of total) <<" % (t_adc_total, t_adc_total/total))
print("Using %d bust sample groups" % (numS))
print("  - ADC Reading Time  = %f (%f p of total) <<" % (t_adc_sample, t_adc_sample/total))
print("  - ADC AvSample Time = %f (%f p of total) <<" % (np.mean(t_adc_per_sample), np.mean(t_adc_per_sample)/total))

print("\nTotal Other Time = %f (%f p of total) <<" % (total-t_dac_spi-t_dac_gpio-t_adc_sample, (total-t_dac_spi-t_dac_gpio-t_adc_sample)/total))

print("\nTime to do all %d readings = %f" % (num_v, total))
print("  - Instance [%d set]/[%d read] average time = %f" % (len(in_pins), len(out_pins), np.mean(t_instance)))
print("  - Instance [%d set]/[%d read] average rate = %f" % (len(in_pins), len(out_pins), 1/np.mean(t_instance)))
print("  - Instance [%d set]/[%d read] average DAC time = %f" % (len(in_pins), len(out_pins), t_dac_total/num_v))
print("  - Instance [%d set]/[%d read] average ADC time = %f" % (len(in_pins), len(out_pins), t_adc_total/num_v))

# fin
