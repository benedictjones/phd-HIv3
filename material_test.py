import numpy as np
from material_Load_meta import LoadMaterialMeta
from material import Material
from material_layer import PiM_processor



# # Load material deets
mdict = LoadMaterialMeta('PiM')
rng = np.random.default_rng(0)

# # Test material
print("\n Material test...")
mobj = Material(mdict)

num_v = 100
s = (num_v , mdict['network']['num_input'] + mdict['network']['num_config'])
Vin = rng.uniform(-5,5, size=s)

print("Vin[0]:\n", Vin[0])

Vout = mobj.solve_material(Vin)
print("Material output[0]:\n", Vout[0])


mobj.fin()





# exit()


# # Test material Layer
print("\n Material Layer test...")
mdict['network']['hiddenSize'] = 2
iM_layer = PiM_processor(mdict)


s = (num_v, mdict['network']['num_input']*mdict['network']['hiddenSize'])
VinD = rng.uniform(-5,5, size=s)

s2 = (mdict['network']['num_config']*mdict['network']['hiddenSize'])
VinC = rng.uniform(-5,5, size=s2)

print(VinD[0],VinC[0])


#exit()

H = iM_layer.solve_layer(VinD,VinC)
print("Layer output:\n", H[0])


iM_layer.fin()


#

#

#

# fin
