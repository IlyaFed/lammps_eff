# it's a common class of all system object
from lib.common_object import *
import numpy as np


class distance_h2(dash_object):
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

        ions = parametrs[parametrs['type'] == 1.0]
        proton_1 = np.array([ions['x'].values[0], ions['y'].values[0], ions['z'].values[0]])
        proton_2 = np.array([ions['x'].values[1], ions['y'].values[1], ions['z'].values[1]])
        electrons = parametrs[parametrs['type'] == 2.0]
        electron_1 = np.array([electrons['x'].values[0], electrons['y'].values[0], electrons['z'].values[0]])
        electron_2 = np.array([electrons['x'].values[1], electrons['y'].values[1], electrons['z'].values[1]])
        center = (proton_1 + proton_2)/2

        self.data.at[Step, "distance_h2_proton_1"] = np.linalg.norm(proton_1-center)
        self.data.at[Step, "distance_h2_proton_2"] = np.linalg.norm(proton_2-center)
        self.data.at[Step, "distance_h2_electron_1"] = np.linalg.norm(electron_1-center)
        self.data.at[Step, "distance_h2_electron_2"] = np.linalg.norm(electron_2-center)

    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []

        traces.append(go.Scatter(
            x = self.data.index,
            y = self.data['distance_h2_proton_1'].values,
            name = 'proton-1',
            mode = 'markers'
        ))
        traces.append(go.Scatter(
            x=self.data.index,
            y=self.data['distance_h2_proton_2'].values,
            name='proton-2',
            mode = 'markers'
        ))
        traces.append(go.Scatter(
            x = self.data.index,
            y = self.data['distance_h2_electron_1'].values,
            name = 'electron-1',
            mode = 'markers'
        ))
        traces.append(go.Scatter(
            x=self.data.index,
            y=self.data['distance_h2_electron_2'].values,
            name='electron-2',
            mode = 'markers'
        ))
        # create line in choosen step
        max_T = max(self.data['distance_h2_proton_1'].max(), self.data['distance_h2_proton_2'].max())
        min_T = min(self.data['distance_h2_proton_1'].min(), self.data['distance_h2_proton_2'].min())
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
            title = 'Distance from center of molecule H2',
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
                title='Distance'
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

    def __init__(self, indexes_of_particle=[]):
        dash_object.__init__(self)
        self.indexes_of_particle = indexes_of_particle # list of 4 elements with h2 particle ids
        self.current_index = 0
        self.graph_type = 'scatter'
        self.name = 'distance_h2'
        self.load_flag = 0
        self.index_list = ['distance_h2_proton_1','distance_h2_proton_2', 'distance_h2_electron_1', 'distance_h2_electron_2']
