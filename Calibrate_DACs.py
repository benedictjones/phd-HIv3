from mod_software.SI import si
import numpy as np
import time
import h5py
import matplotlib.pyplot as plt
from tqdm import tqdm

from scipy.stats import linregress
from datetime import datetime
import os

now = datetime.now()
real_d_string = now.strftime("%d_%m_%Y")
d_string = now.strftime("%Y_%m_%d")
t_string = now.strftime("%H_%M_%S")


# #################################
# Create/Reset calibration data save file
# #################################

# # Location
location = "mod_software/calibrate_data.hdf5"

# # Create the saved hdf5 arrays to hold the calibration data
if os.path.isfile(location) == False:
    with h5py.File(location, 'a') as hdf:
        G_sub = hdf.create_group("Input_Offset")
        G_sub.create_dataset('Constant', data=np.zeros(16))
        G_sub.create_dataset('Gradient', data=np.zeros(16))

        G_sub2 = hdf.create_group("Output_Offset")
        G_sub2.create_dataset('Constant', data=np.zeros(4))
        G_sub2.create_dataset('Gradient', data=np.zeros(4))
else:
    # # Reset
    with h5py.File(location, 'r+') as hdf:
        InOffset_C_bias = hdf.get('/Input_Offset/Constant')
        InOffset_C_bias[:] = np.zeros(16)
        InOffset_G_bias = hdf.get('/Input_Offset/Gradient')
        InOffset_G_bias[:] = np.zeros(16)

        OutOffset_C_bias = hdf.get('/Output_Offset/Constant')
        OutOffset_C_bias[:] = np.zeros(4)
        OutOffset_G_bias = hdf.get('/Output_Offset/Gradient')
        OutOffset_G_bias[:] = np.zeros(4)


# #################################
# Initialte
# #################################

Resitor = 100000 # 47000

# # Create Save Location

save_dir = 'Results/Calibration/DACs/%s__%s' % (d_string, t_string)
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


# # Initiate SI and HI
obj = si(Rshunt=Resitor, electrode3='in', electrode8='in', electrode11='in')  # , electrode3='in'
Rshunt = obj.Rshunt

# # Set the Calibration data to zero
with h5py.File(location, 'r+') as hdf:
    InOffset_C_bias = hdf.get('/Input_Offset/Constant')
    InOffset_G_bias = hdf.get('/Input_Offset/Gradient')


    # ################################
    # Test All DAC outputs
    # ################################
    pins = np.arange(1, 16)
    print("Pins to sweep over:", pins)
    OP = 4

    interval = 0.02  # 0.05
    x1_max = 9
    Vin_sweep = np.arange(-x1_max, x1_max+interval, interval)



    for i, pin in enumerate(pins):

        print("\nConnect pin %d to OP %d..." % (pin, OP))
        answer = (input("Enter anything to continue (enter e to exit): " ))
        if str(answer) == 'e':
            break
        else:
            pass


        Vdiff = []
        Vouts = []
        for v in tqdm(Vin_sweep):
            v = np.round(v,4)
            obj.SetVoltage(electrode=pin, voltage=v)
            Vop = obj.ReadVoltage(OP, debug=0, nSamples=30)  # ch0, pin3, op1
            Vd = v - Vop
            Vdiff.append(Vd)
            Vouts.append(Vop)


        # # save data
        location = "%s/data_In%d_OP%d.hdf5" % (save_dir, pin, OP)
        with h5py.File(location, 'a') as hdf:
            G_sub = hdf.create_group("IO")

            G_sub.create_dataset('Vin', data=Vin_sweep)
            G_sub.create_dataset('Vout', data=Vouts)
            G_sub.create_dataset('Vdiff', data=Vdiff)

        reg = linregress(x=Vin_sweep, y=Vdiff)
        print("y = m*x + c")
        print("Vdiff = %f*Vin + %f :" % (reg.slope, reg.intercept))
        InOffset_C_bias[i] = reg.intercept
        InOffset_G_bias[i] = reg.slope

        """ # # Plot data
        fig = plt.figure()
        plt.plot(Vin_sweep, Vouts, label='V')
        plt.legend()
        plt.xlabel('Vin')
        plt.ylabel('Vout')
        plt.title('Voltage sweep being directly read')
        fig_path = "%s/FIG_In%d_OP%d_VinVout.png" % (save_dir, pin, OP)
        fig.savefig(fig_path, dpi=300)
        # """

        fig = plt.figure()
        plt.plot(Vin_sweep, Vdiff, 'o', label='V')
        plt.legend()
        plt.xlabel('Vin')
        plt.ylabel('Vdiff = Vin - Vout')
        plt.title('Voltage sweep being directly read\nVdiff = %f*Vin + %f :' % (reg.slope, reg.intercept))
        fig_path = "%s/FIG_In%d_OP%d_VinVdiff.png" % (save_dir, pin, OP)
        fig.savefig(fig_path, dpi=200)
        plt.close(fig)
        
obj.fin()

print("Calibration Finished")

#

#

#

#

#

#

print("Retesting with calibration...")



# # Initiate SI and HI
obj2 = si(Rshunt=Resitor, electrode3='in', electrode8='in', electrode11='in')  # , electrode3='in'
Rshunt = obj2.Rshunt

# ################################
# Test All DAC outputs
# ################################
print("Pins to sweep over:", pins)
OP = 4

interval = 0.02 # 0.05
x1_max = 9
Vin_sweep = np.arange(-x1_max, x1_max+interval, interval)



for i, pin in enumerate(pins):

    print("\nConnect pin %d to OP %d..." % (pin, OP))
    answer = (input("Enter anything to continue (enter e to exit): " ))
    if str(answer) == 'e':
        break
    else:
        pass


    Vdiff = []
    Vouts = []
    for v in tqdm(Vin_sweep):
        v = np.round(v,4)
        obj2.SetVoltage(electrode=pin, voltage=v)
        Vop = obj2.ReadVoltage(OP, debug=0, nSamples=30)  # ch0, pin3, op1
        Vd = v - Vop
        Vdiff.append(Vd)
        Vouts.append(Vop)


    reg = linregress(x=Vin_sweep, y=Vdiff)

    fig = plt.figure()
    plt.plot(Vin_sweep, Vdiff, 'o', label='V')
    plt.legend()
    plt.xlabel('Vin')
    plt.ylabel('Vdiff = Vin - Vout')
    plt.title('Voltage sweep being directly read\nVdiff = %f*Vin + %f :' % (reg.slope, reg.intercept))
    fig_path = "%s/FIG_In%d_OP%d_VinVdiff_CORRECTED.png" % (save_dir, pin, OP)
    fig.savefig(fig_path, dpi=200)
    plt.close(fig)

obj2.fin()

print("Finished!")

#

#

# fin
