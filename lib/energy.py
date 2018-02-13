# it's a common class of all system object
from lib.common_object import *
import numpy as np


class energy(dash_object):
    def load_step(self, Step, parametrs):
        '''
        Here we upload step data and put it into data structure
        '''
        if self.load_flag:
            return 0
        k_boltz = 1.3806485279e-23
        e_hartry = 27.2113845
        # read ions temp
        def sum_f(x):
            return (x['c_peatom'] + x['c_keatom']) * e_hartry
        ion = parametrs[parametrs['type'] == 1.0].apply(sum_f, axis = 1).sum()
        electron = parametrs[parametrs['type'] == 2.0].apply(sum_f, axis = 1).sum()
        self.data.loc[len(self.data)] = [Step, ion, electron, ion + electron]

    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []

        traces.append(go.Scatter(
            x = self.data['Step'].values,
            y = self.data['ion'].values,
            name = 'ions',
            mode = 'line'
        ))
        traces.append(go.Scatter(
            x=self.data['Step'].values,
            y=self.data['electron'].values,
            name='electrons',
            mode = 'line',
        ))

        traces.append(go.Scatter(
            x=self.data['Step'].values,
            y=self.data['all'].values,
            name='full',
            mode = 'line'
        ))
        # create line in choosen step
        max_T = max(self.data['ion'].max(), self.data['electron'].max(), self.data['all'].max())
        min_T = min(self.data['ion'].min(), self.data['electron'].min(), self.data['all'].min())
        step = self.data.loc[self.current_index, 'Step']
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
        return go.Layout(
            showlegend = True,
            width=500,
            height=300,
            title = 'Energy of system',
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

    def __init__(self):
        self.data = pd.DataFrame(columns=["Step", "ion", "electron", "all"])
        self.current_index = 0
        self.graph_type = 'scatter'
        self.name = 'energy'
