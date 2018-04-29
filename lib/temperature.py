# it's a common class of all system object
from lib.common_object import *
import numpy as np


class temperature(dash_object):
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
        our_param = parametrs[parametrs['type'] == 1.0]
        ion = 2. / 3. / k_boltz *  (our_param['c_keatom'].mean() * e_harty)
        # read electron temp
        our_param = parametrs[parametrs['type'] == 2.0]
        electron = 2. / 4. / k_boltz * (our_param['c_keatom'].mean() * e_harty)
        self.data.at[ind, 'temp_ion'] = ion
        self.data.at[ind, 'temp_electron'] = electron
    
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


        self.data.at[ind, 'temp_ion'] = ion
        self.data.at[ind, 'temp_electron'] = electron

    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []

        traces.append(go.Scatter(
            x = self.data.index,
            y = self.data['temp_ion'].values,
            name = 'ions',
            mode = 'line'
        ))
        traces.append(go.Scatter(
            x=self.data.index,
            y=self.data['temp_electron'].values,
            name='electrons',
            mode = 'line'
        ))
        # create line in choosen step
        max_T = max(self.data['temp_ion'].max(), self.data['temp_electron'].max())
        min_T = min(self.data['temp_ion'].min(), self.data['temp_electron'].min())
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
            title = 'Temperature of system',
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
                title='Temperature, K'
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

    def __init__(self):
        dash_object.__init__(self)
        self.current_index = 0
        self.graph_type = 'scatter'
        self.name = 'temperature'
        self.load_flag = 0
        self.index_list = ['temp_ion', 'temp_electron']
