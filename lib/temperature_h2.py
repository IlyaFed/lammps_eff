# it's a common class of all system object
from lib.common_object import *
import numpy as np


class temperature_h2(dash_object):
    def analyse(self, data, gen_info):
        self.data = data
        self.gen_info = gen_info
        self.timestep = self.gen_info['timestep']
        self.mass = self.gen_info['mass']

        load_flag = 1
        for item in self.index_list:
            if not item in self.data.columns:
                load_flag = 0
        if load_flag:
            return 0

        for Step in self.data.index:
            self.load_step(Step)
        return 1


    def load_step(self, Step):
        parametrs = self.data.loc[Step, 'every']
        parametrs = parametrs[(parametrs['id'].isin(self.indexes_of_particle))] # just this H2
        '''
        Here we upload step data and put it into data structure
        '''
        if 'c_keatom' in parametrs.columns:
            self.fast_load(Step, parametrs)
        else:
            self.slow_load(Step, parametrs)
    
    def fast_load(self, ind, parametrs):
        '''
        We analyse kinetic energy of particle to introduce temperature
        '''
        k_boltz = 1.3806485279e-23
        e_harty = 4.35974417e-18
        # read ions temp
        #print ("id = ", parametrs[(parametrs['id'].isin(self.indexes_of_particle))]['id'])
        ion_1 = parametrs[parametrs['id'] == ions[0]]['c_keatom'].values[0]
        ion_2 = parametrs[parametrs['id'] == ions[1]]['c_keatom'].values[0]
        electron_1 = parametrs[parametrs['id'] == electrons[0]]['c_keatom'].values[0]
        electron_2 = parametrs[parametrs['id'] == electrons[1]]['c_keatom'].values[0]
        if self.type_T == 'T':
            ion_1 = 2. / 3. / k_boltz *  (ion_1 * e_harty)
            ion_2 = 2. / 3. / k_boltz *  (ion_2 * e_harty)
            electron_1 = 2. / 4. / k_boltz *  (electron_1 * e_harty)
            electron_2 = 2. / 4. / k_boltz *  (electron_2 * e_harty)
        # read electron temp
        self.data.at[ind, 'temp_h2_ion_1'] = ion_1
        self.data.at[ind, 'temp_h2_ion_2'] = ion_2
        self.data.at[ind, 'temp_h2_electron_1'] = electron_1
        self.data.at[ind, 'temp_h2_electron_2'] = electron_2
    
    def slow_load(self, ind, parametrs):
        '''
        We analyse velosity of particles to introduce temperature
        '''
        k_boltz = 1.3806485279e-23 # e-23
        bohr = 0.5291772e-10
        Avogadro = 6.022141e23
        atu = 1.03275e-15
        
        # electron part
        our_param = parametrs[parametrs['type'] == 2.0]
        def f_T_electron(param):
            v2 = param['vx']**2 + param['vy']**2 + param['vz']**2
            rad_v2 = param['c_1a[3]']**2
            return v2 + 0.75 * rad_v2
        kin_energy = 0.5 * our_param.apply(f_T_electron, axis=1).mean() * (bohr/atu)**2  * (self.mass[1] * 1e-3 / Avogadro)
        # in the energy equation we expect that mass in gramm
        electron = 2. / 4. / k_boltz * kin_energy

        # ion part
        our_param = parametrs[parametrs['type'] == 1.0]
        def f_T_ion(param):
            v2 = param['vx']**2 + param['vy']**2 + param['vz']**2
            return v2
        kin_energy = 0.5 * our_param.apply(f_T_ion, axis=1).mean() * (bohr/atu)**2  * (self.mass[0] * 1e-3 / Avogadro)
        ion =  2. / 3. / k_boltz * kin_energy


        self.data.at[ind, 'temp_ion_h2'] = ion
        self.data.at[ind, 'temp_electron_h2'] = electron

    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []

        traces.append(go.Scatter(
            x = self.data.index,
            y = self.data['temp_h2_ion_1'].values,
            name = 'ion_1',
            mode = 'line'
        ))
        traces.append(go.Scatter(
            x=self.data.index,
            y=self.data['temp_h2_electron_1'].values,
            name='electron_1',
            mode = 'line'
        ))
        traces.append(go.Scatter(
            x = self.data.index,
            y = self.data['temp_h2_ion_2'].values,
            name = 'ion_2',
            mode = 'line'
        ))
        traces.append(go.Scatter(
            x=self.data.index,
            y=self.data['temp_h2_electron_2'].values,
            name='electron_2',
            mode = 'line'
        ))
        # create line in choosen step
        max_T = max(self.data['temp_h2_ion_1'].max(), self.data['temp_h2_electron_1'].max())
        min_T = min(self.data['temp_h2_ion_1'].min(), self.data['temp_h2_electron_1'].min())
        step = self.current_index
        traces.append(go.Scatter(
            x = np.linspace(step, step, 100),
            y = np.linspace(min_T, max_T, 100),
            name = 'current step'
        ))

        return traces

    def __get_trace(self):
        if self.graph_type == 'scatter':
            return self.__get_scatter_trace()
    def __get_layout(self):
        return go.Layout(
            showlegend = True,
            width=500,
            height=300,
            title = 'Temperature of H2 molecule',
            xaxis = dict(
                showgrid = True,
                zeroline = False,
                showline = True,
                title = 'Step'
            ),
            yaxis=dict(
                showgrid=True,
                zeroline=False,
                showline=True,
                title=self.type_T + ', K'
            )
        )
    def _update_graph(self):
        '''
        Here we update graph with neccessary parametrs
        :return:
        '''
        traces = self.__get_trace()
        layout = self.__get_layout()
        return {
            'data': traces,
            'layout': layout
        }

    def get_html(self):
        '''
        Here we describe frontend of our object
        '''
        layout = html.Div(
                    dcc.Graph(
                        id=self.name,
                        ),
                    style = {'width': '49%', 'display': 'inline-block'}
                    )
        return layout

    def __init__(self, ions=[], electrons=[], type_T="T"):
        dash_object.__init__(self)
        self.type_T=type_T
        self.indexes_of_particle = ions + electrons
        self.ions = ions
        self.electrons = electrons
        self.current_index = 0
        self.graph_type = 'scatter'
        self.name = 'temperature_h2'
        self.load_flag = 0
        self.index_list = ['temp_h2_ion_1', 'temp_h2_electron_1', 'temp_h2_ion_2', 'temp_h2_electron_2']
