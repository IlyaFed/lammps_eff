# it's a common class of all system object
from lib.common_object import *
import numpy as np


class pt_diagram(dash_object):
    def load_log(self, parametrs):
        '''
        Here we upload step data and put it into data structure
        '''
        if self.load_flag:
            return 0
        self.data = pd.concat([parametrs['Step'], parametrs['Temp'], parametrs['Press']], axis = 1, keys = ['Step', 'Temp', 'Press'])

    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []

        traces.append(go.Scatter(
            x=self.data['Press'].values/1e9, # GPa
            y=self.data['Temp'].values,
            mode = 'marker',
            name = 'Data'
        ))

        # create line in choosen step
        max_T = max(self.data['Temp'].max(), self.data['Temp'].max())
        min_T = min(self.data['Temp'].min(), self.data['Temp'].min())


        for item in list(self.experimental_data.keys()):
            traces.append(go.Scatter(
            x=self.experimental_data[item][1],
            y=self.experimental_data[item][0],
            mode = 'marker',
            name = item
            ))
            max_T = max(max_T, max(self.experimental_data[item][0]))
            min_T = max(min_T, min(self.experimental_data[item][0]))

        press = self.data.loc[self.current_index, 'Press']
        traces.append(go.Scatter(
            x = np.linspace(press, press, 100),
            y = np.linspace(min_T, max_T, 100),
            name = 'current step'
        ))

        return traces

    def __get_trace(self):
        if self.graph_type == 'scatter':
            return self.__get_scatter_trace()

    def __get_layout(self):
        return go.Layout(
            showlegend = False,
            title = 'PT diagram',
            xaxis = dict(
                showgrid = True,
                zeroline = False,
                showline = True,
                title = 'Pressure, GPa'
            ),
            yaxis=dict(
                type='log',
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

    def __init__(self, experimental_data = dict()):
        self.current_index = 0
        self.graph_type = 'scatter'
        self.name = 'PT'
        self.experimental_data = experimental_data
