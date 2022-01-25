from mod_software.SI import si
import numpy as np
import time
import h5py
import matplotlib.pyplot as plt

from scipy.stats import linregress

import os
from datetime import datetime



obj = si(Rshunt=14000)  # 14000

Rshunt = obj.Rshunt

# #################################
now = datetime.now()
real_d_string = now.strftime("%d_%m_%Y")
d_string = now.strftime("%Y_%m_%d")
print("Date:", real_d_string)
print("Date:", d_string)
t_string = now.strftime("%H_%M_%S")
print("Time Stamp:", t_string, "\n\n")



p = 1
OP = 4

test_label = 'IO_sweep__p%s_Op%d' % (p,OP)
test_label = 'IO_sweep__NWs_23_partner'
test_label = 'IO_sweep__Test_1p2M_14kShunt'

#test_label = 'IO_sweep__NWs'
#test_label = 'pks'

save_dir = "Results/%s/%s_%s" % (d_string, t_string, test_label)
os.makedirs(save_dir)

# ################################


interval = 0.05 # 0.05
x1_max = 5
Vin = np.arange(-x1_max, x1_max+interval, interval)

# Vin = [0, 0, 0, 0, 0, 0, 0, 0]

Vin_sweep = np.concatenate((Vin, np.flip(Vin)))
Vin_sweep = np.concatenate((np.flip(Vin),Vin))

print("Num write/reads for 2 loops:", 2*len(Vin_sweep))

Vout = []
Iout = []

obj.ElectrodeState()

input("Press Enter to continue... ")


for v in Vin_sweep:

    v = np.round(v,3)

    obj.SetVoltage(electrode=p, voltage=v)
    #time.sleep(2)
    # op = obj.ReadVoltage(OP, debug=0)  # ch0, pin3, op1

    Iop, Vop = obj.ReadIV(OP)


    Vout.append(Vop)
    Iout.append(Iop)
    print("Vin=", v, " Vout=", Vop, ",  I=", Iop)
    #input("Press Enter to move to next input V")

# Second sweep
Vout2 = []
Iout2 = []
for v in Vin_sweep:

    v = np.round(v,3)

    obj.SetVoltage(electrode=p, voltage=v)
    # time.sleep(0.1)
    # op = obj.ReadVoltage(OP)  # ch0, pin3, op1

    Iop, Vop = obj.ReadIV(OP)


    Vout2.append(Vop)
    Iout2.append(Iop)
    print("Vin=", v, " Vout=", Vop, ",  I=", Iop)
    #input("Press Enter to move to next input V")


obj.fin()
Vout = np.asarray(Vout)



# save data
location = "%s/data.hdf5" % (save_dir)
with h5py.File(location, 'a') as hdf:
    G_sub = hdf.create_group("IO")

    G_sub.create_dataset('Vin', data=Vin_sweep)
    G_sub.create_dataset('Vout', data=Vout)
    G_sub.create_dataset('Vout2', data=Vout2)
    G_sub.create_dataset('Iout', data=Iout)
    G_sub.create_dataset('Iout2', data=Iout2)



# estimate gradient of first half of forward sweep
glim = int(len(Vin)/4)




# # Calc Material Resitance
print("\nCalc Material Resitance")
print(" > Rshunt = ", Rshunt)

reg = linregress(Vout[:glim], (Vin[:glim]))
print("x(out) y(Vin) slope:", reg.slope)

reg = linregress(x=Vin[:glim], y=Vout[:glim])
print("x(Vin) y(Vout) slope:", reg.slope)

# Rm = reg.slope - 70 # old now wrong
if Rshunt == 'none':
    Rm = np.nan
else:
    Rm = Rshunt/reg.slope - Rshunt
    print("\n Vgrad to Vgrad calc")
    print("For pin to op, Rmaterial ~", Rm)


# # Current dereived
if Rshunt == 'none':
    Rm = np.nan
else:
    print("\n IV grad calc")
    reg = linregress(x=Vin[:glim], y=Iout[:glim])
    print("x(Vin) y(Iout) slope:", reg.slope)
    print("1/x=", 1/reg.slope)
    Rm = (1/reg.slope) - Rshunt
    print("For pin to op1, Rmaterial ~", Rm)




figI = plt.figure()
plt.plot(Vin_sweep, Iout, label='sweep 1')
plt.plot(Vin_sweep, Iout2, label='sweep 2')
plt.legend()
plt.xlabel('Vin')
plt.ylabel('Iout')
plt.title('Directly connected IO (set value vs read value)\n Rmaterial ~ %f' % (Rm))
fig_path = "%s/FIG_Iout.png" % (save_dir)
figI.savefig(fig_path, dpi=300)

figV = plt.figure()
plt.plot(Vin_sweep, Vout, label='sweep 1')
plt.plot(Vin_sweep, Vout2, label='sweep 2')
plt.legend()
plt.xlabel('Vin')
plt.ylabel('Vout')
plt.title('Directly connected IO (set value vs read value)\n Rmaterial ~ %f' % (Rm))
fig_path = "%s/FIG_Vout.png" % (save_dir)
figV.savefig(fig_path, dpi=300)

plt.show()
plt.close('all')



# fin
