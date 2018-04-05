# it's a common class of all system object
from lib.common_object import *
import numpy as np

class energy(dash_object):
    def analyse(self, data, gen_info):
        self.data = data
        self.gen_info = gen_info
        self.timestep = self.gen_info['timestep']

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
        k_boltz = 1.3806485279e-23
        e_hartry = 27.2113845
        # read ions temp
        if self.type == 'kinetic':
            def sum_f(x):
                return x['c_keatom'] * e_hartry
        if self.type == 'potential':
            def sum_f(x):
                return x['c_peatom'] * e_hartry
        if self.type == 'full':
            def sum_f(x):
                return (x['c_peatom'] + x['c_keatom']) * e_hartry

        ion = parametrs[parametrs['type'] == 1.0].apply(sum_f, axis = 1).sum()
        electron = parametrs[parametrs['type'] == 2.0].apply(sum_f, axis = 1).sum()
        self.data.at[Step, self.type + "_ion"] = ion
        self.data.at[Step, self.type + "_electron"] = electron
        self.data.at[Step, self.type + "_all"] = ion + electron

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
            y=self.data[self.type + "_ion"].values,
            name='ions',
            mode='line'
        ))
        traces.append(go.Scatter(
            x=x_step,
            y=self.data[self.type + '_electron'].values,
            name='electrons',
            mode='line',
        ))

        traces.append(go.Scatter(
            x=x_step,
            y=self.data[self.type + '_all'].values,
            name='full',
            mode='line'
        ))
        # create line in choosen step
        max_T = max(self.data[self.type + '_ion'].max(), self.data[self.type + '_electron'].max(), self.data[self.type + '_all'].max())
        min_T = min(self.data[self.type + '_ion'].min(), self.data[self.type + '_electron'].min(), self.data[self.type + '_all'].min())
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
            title = self.type + ' energy of system',
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

    def _internal_callback(self):
        '''
        Here we explain all callback which caused bu internal parametrs changes
        '''

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


    def __init__(self, type = 'full'):
        self.type = type
        self.current_index = 0
        self.graph_type = 'scatter'
        self.name = 'energy' + self.type
        self.index_list = [self.type + "_ion", self.type + "_electron", self.type + "_all"]
