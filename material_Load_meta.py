import yaml
import numpy as np
''' # Load and return the settings parameter dictionary from file
'''


def LoadMetaData(dir, param_file=''):

    with open(r'%s/Experiment_MetaData%s.yaml' % (dir, param_file)) as file:
        # MetaData = yaml.full_load(file)  # broken with classweight obj load
        MetaData = yaml.load(file, Loader=yaml.Loader)

    return MetaData


def LoadMaterialMeta(type):

    if 'SiM' in type:
        file = 'mod_SiM/material.yaml'
    elif 'PiM' in type:
        file = 'mod_PiM/material.yaml'

    #

    with open(r'%s' % file) as file:
        # MetaData = yaml.full_load(file)  # broken with classweight obj load
        md = yaml.load(file, Loader=yaml.Loader)

    #

    # # Deal with SiM Specific alterations
    if 'SiM' in type:
        if md['network']['mseed'] != 'na':
            rng = np.random.default_rng(md['network']['mseed'])
        else:
            rng = np.random.default_rng()
        md['network']['mseeded'] = rng.integers(100000, size=1)[0]

    # # Deal with PiM Specific alterations & checks
    elif 'PiM' in type:
        if len(md['spice']['in_pins']) != (md['network']['num_input']+md['network']['num_config']):
            raise ValueError("Number of input voltage pins %d does not match the desired number of input (%d) and config (%d) pins" % (len(md['spice']['in_pins']), md['network']['num_input'], md['network']['num_config']))

        if len(md['spice']['out_pins']) != md['network']['num_output']:
            raise ValueError("Number of output voltage pins %d does not match the desired number of output netowrk nodes %d" % (len(md['spice']['out_pins']), md['network']['num_output']))


    md['network']['num_nodes'] = md['network']['num_input'] + md['network']['num_config'] + md['network']['num_output']


    return md
#

# fin
