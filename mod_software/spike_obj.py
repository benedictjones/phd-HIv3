import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FormatStrFormatter
import itertools
from mpl_toolkits import mplot3d

import mpl_toolkits.mplot3d.axes3d as p3

import numpy as np

from collections import namedtuple



class spike_trains(object):

    #

    def __init__(self, **kwargs):
        ''' # # # # # # # # # # # # # # #
        Initialisation of class
        '''

        self.pars = {}
        self.pars['encoding'] = 'temporal'
        self.pars['t_max'] = 0.5
        self.pars['dt'] = self.pars['t_max']/1000
        self.pars['t_pulse'] = 0.01# 0.005 #self.pars['t_max']/20 # 0.001


        # external parameters if any #
        for k in kwargs:
            self.pars[k] = kwargs[k]

        # # Check the self.pars['encoding'] type
        if self.pars['encoding'] != 'rate' and self.pars['encoding'] != 'temporal':
            raise ValueError("Only two available types of spike self.pars['encoding'], %s is invalid" % (str(self.pars['encoding'])))

        return

    #

    def encode(self, value, ret='simple'):
        ''' # # # # # # # # # # # # # # #
        Initialisation of class
        '''

        # # Check Lims
        if abs(value) > 1:
            raise ValueError("Input instance is too large")

        # # Encode
        if self.pars['encoding'] == 'rate':
            Time, V, spike_time, Vpeak, spike_train = self._rate_encoding_(value)
        elif self.pars['encoding'] == 'temporal':
            Time, V, spike_time, Vpeak, spike_train = self._temporal_encoding_(value)

        ST = namedtuple('ST', ['time', 'spike_train', 'spike_time', 'V', 'Vpeak'])
        st = ST(Time, spike_train, spike_time, V, Vpeak)

        return st


    #

    def _rate_encoding_(self, ist):

        neg = 0
        if ist < 0:
            neg = 1
            ist = abs(ist)

        # # Params
        C = 1
        I = 1
        Vreset = 0
        t = 0
        Tr = self.pars['t_pulse']/10  # the count for refractory duration (pause after a spike)

        Vth = ist*self.pars['t_max']*(I/C)
        V = [Vth]
        Time = [0]

        # # Start Loop
        spike_continuous = [0]
        spike = []
        tr = 0
        tp = 0
        while t < self.pars['t_max']:

            # # Apply the refactory period or update
            if tp <= 0 and tr > 0:
                v = Vreset
                tr = tr - self.pars['dt']
            else:
                v = V[-1] + self.pars['dt']*(I/C)  # Update the voltage,

            if v >= Vth: # ... and check if the voltage exceeds the threshold.

                if tp <= self.pars['t_pulse']:
                    v = Vth
                    tp += self.pars['dt']
                else:
                    v = Vreset
                    tp = 0

                spike.append(Time[-1])
                tr = Tr
                spike_continuous.append(1)
            else:
                spike_continuous.append(0)

            V.append(v)
            Time.append(t)
            t = t + self.pars['dt']

        Vpeak = np.max(V)
        if neg:
            V = np.array(V)*-1
            Vpeak = Vpeak*-1
            spike_continuous = np.array(spike_continuous)*-1

        return tuple(Time), V, tuple(spike), Vpeak, tuple(spike_continuous)

    #

    def _temporal_encoding_(self, ist):

        neg = 0
        if ist < 0:
            neg = 1
            ist = abs(ist)


        T = (self.pars['t_max']-self.pars['t_pulse'])*ist
        t = 0
        # Tr = self.pars['t_max']/20  # the count for refractory duration (pause after a spike)

        # # begin loop
        V = [0]
        Time = [0]
        spike_continuous = [0]
        spike = []
        while t < self.pars['t_max']:

            # # Spike or note
            if ((t >= T-self.pars['dt']/2) and (t <= T+self.pars['t_pulse']+self.pars['dt']/2)):
                v = 1
                spike.append(Time[-1])
                spike_continuous.append(1)
            else:
                v = 0
                spike_continuous.append(0)
                # good_hit = 0

            V.append(v)
            Time.append(t)

            t = t + self.pars['dt']

        Vpeak = np.max(V)
        if neg:
            V = np.array(V)*-1
            Vpeak = Vpeak*-1
            spike_continuous = np.array(spike_continuous)*-1

        return tuple(Time), V, tuple(spike), Vpeak, tuple(spike_continuous)





"""
clrs = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']




instance = [0.1, 1, 0.5, -0.3]
#instance = [0.01, 0.1, 1]

sobj = spike_trains(encoding='rate')  # rate, temporal

#'''
plt.figure()
for i, ist in enumerate(instance):
    st = sobj.encode(ist)
    plt.plot(st.time, st.V, label=str(ist), color=clrs[i])
    plt.plot(st.spike_time, np.ones(len(st.spike_time))*st.Vpeak, 'x', color=clrs[i])
plt.xlabel('Time [s]')
plt.ylabel('V')
plt.legend()
plt.title('Rate Based')
#'''

plt.figure()
for i, ist in enumerate(instance):
    st = sobj.encode(ist)

    plt.plot(st.time , st.spike_train, label=str(ist), color=clrs[i], alpha=0.7)
plt.xlabel('Time [s]')
plt.ylabel('Spike')
plt.title('Rate Based')
plt.legend()

# #######################################


sobj2 = spike_trains(encoding='temporal')  # rate, temporal

#'''
plt.figure()
for i, ist in enumerate(instance):
    st = sobj2.encode(ist)
    plt.plot(st.time, st.V, label=str(ist), color=clrs[i])
    plt.plot(st.spike_time, np.ones(len(st.spike_time))*st.Vpeak, 'x', color=clrs[i])
plt.xlabel('Time [s]')
plt.ylabel('V')
plt.legend()
plt.title('temporal Based')
#'''

plt.figure()
for i, ist in enumerate(instance):
    st = sobj2.encode(ist)

    plt.plot(st.time , st.spike_train, label=str(ist), color=clrs[i], alpha=0.7)
plt.xlabel('Time [s]')
plt.ylabel('Spike')
plt.title('temporal Based')
plt.legend()

plt.show()
"""
#

# fin
