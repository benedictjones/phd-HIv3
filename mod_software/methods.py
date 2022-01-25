import numpy as np
import time
from tqdm import tqdm
from datetime import datetime




def run_voltage_sweep(siobj, x1_array, x2_array, in_pins, op_pins, config_pins, config):

    if len(config) != len(config_pins):
        siobj.fin()
        raise ValueError("Invalid config in array")

    rY = np.zeros((len(x1_array),len(x2_array)))
    Vop_unshaped = []

    if config_pins != 'na':
        for i, c_pin in enumerate(config_pins):
            siobj.SetVoltage(electrode=c_pin, voltage=config[i])

    for idx1, x1 in enumerate(tqdm(x1_array)):

        for idx2, x2 in enumerate(x2_array):

            # set voltages
            siobj.SetVoltage(electrode=in_pins[0], voltage=x1)
            siobj.SetVoltage(electrode=in_pins[1], voltage=x2)
            time.sleep(0.01)
            Vop1 = siobj.ReadVoltage(op_pins[0], loc_scheme='electrode')
            Vop2 = siobj.ReadVoltage(op_pins[1], loc_scheme='electrode')

            rY[idx1, idx2] = Vop1 + Vop2
            Vop_unshaped.append([Vop1, Vop2])

    Vop_unshaped = np.asarray(Vop_unshaped)

    ops = []
    for op_node in range(len(Vop_unshaped[0,:])):
        ops.append(np.reshape(Vop_unshaped[:, op_node], (len(x1_array), len(x2_array))))

    return rY, ops
