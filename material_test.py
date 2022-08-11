import numpy as np
from material_Load_meta import LoadMaterialMeta
from material import Material
from material_layer import PiM_processor



# # Load material deets
mdict = LoadMaterialMeta('PiM')

# # Test material
mobj = Material(mdict)

num_v = 10
s = (num_v , mdict['network']['num_input'] + mdict['network']['num_config'])
Vin = np.uniform(-2,2, size=s)

Vout = mobj.solve_material(Vin)
print("Material output:\n", Vout)


mobj.fin()





exit()


# # Test material Layer
mdict['network']['hiddenSize'] = 2
iM_layer = PiM_processor(mdict)


s = (num_v, (mdict['network']['num_input']+mdict['network']['num_config'])*mdict['network']['hiddenSize'])
Vin = np.uniform(-2,2, size=s)

H = iM_layer.solve_layer(Vin)
print("Layer output:\n", H)


iM_layer.fin()


#

#

#

# fin
