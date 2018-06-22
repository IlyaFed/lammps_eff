# it's a common class of all system object
from lib.common_object import *
import numpy as np


class energy_h2(dash_object):
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
        k_boltz = 1.3806485279e-23
        e_hartry = 27.2113845
        # read ions temp
        
        if self.type == 'potential':
            if 'c_peatom' in parametrs.columns:
                def sum_f(x):
                    return x['c_peatom'] * e_hartry
            else:
                print ("error: no {:s} in data".format('c_peatom'))
                def sum_f(x):
                    return 0
        elif self.type == 'full':
            if ('c_keatom' in parametrs.columns) or ('c_peatom' in parametrs.columns):
                def sum_f(x):
                    return (x['c_peatom'] + x['c_keatom']) * e_hartry
            else:
                print ("error: no need data in data")
                def sum_f(x):
                    return 0

        ion_1 = parametrs[parametrs['id'] == self.ions[0]].apply(sum_f, axis = 1).sum()
        ion_2 = parametrs[parametrs['id'] == self.ions[1]].apply(sum_f, axis = 1).sum()
        electron_1 = parametrs[parametrs['id'] == self.electrons[0]].apply(sum_f, axis = 1).sum()
        electron_2 = parametrs[parametrs['id'] == self.electrons[1]].apply(sum_f, axis = 1).sum()
        self.data.at[Step, self.type + "h2_ion_1"] = ion_1
        self.data.at[Step, self.type + "h2_ion_2"] = ion_2
        self.data.at[Step, self.type + "h2_electron_1"] = electron_1
        self.data.at[Step, self.type + "h2_electron_2"] = electron_2
        self.data.at[Step, self.type + "h2_all"] = ion_1 + ion_2 + electron_1 + electron_2


    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []
        if self.timestep == 0:
            x_step = self.data.index
            step = self.current_index
        else:
            x_step = self.data.index * self.timestep
            step = self.current_index * self.timestep

        traces.append(go.Scatter(
            x=x_step,
            y=self.data[self.type + "h2_ion_1"].values,
            name='ion_1',
            mode='line'
        ))
        traces.append(go.Scatter(
            x=x_step,
            y=self.data[self.type + 'h2_electron_1'].values,
            name='electron_1',
            mode='line',
        ))

        traces.append(go.Scatter(
            x=x_step,
            y=self.data[self.type + "h2_ion_2"].values,
            name='ion_2',
            mode='line'
        ))
        traces.append(go.Scatter(
            x=x_step,
            y=self.data[self.type + 'h2_electron_2'].values,
            name='electron_2',
            mode='line',
        ))

        traces.append(go.Scatter(
            x=x_step,
            y=self.data[self.type + 'h2_all'].values,
            name='full',
            mode='line'
        ))
        # create line in choosen step
        max_T = max(self.data[self.type + 'h2_ion_1'].max(), self.data[self.type + 'h2_electron_1'].max(), self.data[self.type + 'h2_all'].max())
        min_T = min(self.data[self.type + 'h2_ion_1'].min(), self.data[self.type + 'h2_electron_1'].min(), self.data[self.type + 'h2_all'].min())
        traces.append(go.Scatter(
            x = np.linspace(step, step, 100),
            y = np.linspace(min_T, max_T, 100),
            name = 'current step',
            mode='line'
        ))

        return traces

    def __get_trace(self):
        if self.graph_type == 'scatter':
            return self.__get_scatter_trace()
    def __get_layout(self):
        if self.timestep == 0:
            x_title = "Step"
        else:
            x_title = "Time, fs"
        return go.Layout(
            showlegend = True,
            width=500,
            height=300,
            title = self.type + ' energy of h2',
            xaxis = dict(
                showgrid = True,
                zeroline = False,
                showline = True,
                title = x_title
            ),
            yaxis=dict(
                showgrid=True,
                zeroline=False,
                showline=True,
                title='Energy, eV'
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

    def __init__(self, type = 'full', ions=[], electrons=[]):
        dash_object.__init__(self)
        self.type = type
        self.indexes_of_particle = ions + electrons
        self.ions = ions
        self.electrons = electrons
        self.current_index = 0
        self.graph_type = 'scatter'
        self.name = 'energy_h2'+self.type
        self.load_flag = 0
        self.index_list = [self.type + "h2_ion_1", self.type + "h2_ion_2", self.type + "h2_electron_1",self.type + "h2_electron_2", self.type + "h2_all"]
