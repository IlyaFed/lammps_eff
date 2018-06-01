# it's a common class of all system object
from lib.common_object import *
import numpy as np


class common_neighbour_distribtution(dash_object):
    def analyse(self, system_objects):
        self.info = []
        for path in system_objects:
            if not self.common_phrase in path: #filtered for rho TODO
                continue
            if system_objects[path].is_ready():
                self.info.append(system_objects[path].info())
        if len(self.info):
            self.analysed_flag = 1
        '''
        Here we upload step data and put it into data structure
        '''
        return 0

    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []

        for sys_info in self.info:
            data = sys_info['data']
            geninfo = sys_info['info']
            N = data.loc[data.index[0], 'every'].shape[0]
            traces.append(go.Scatter(
                x=data['Press'].values[1:], # GPa
                y=data['H2'].values[1:]/N*100, #[1:] - because first one is wrong
                mode = 'line',
                name = geninfo['title']
            ))


          
        return traces

    def __get_trace(self):
        if self.graph_type == 'scatter':
            return self.__get_scatter_trace()

    def __get_layout(self):
        return go.Layout(
            showlegend = True,
            title = 'Common neighbour distribution for ' + self.common_phrase,
            xaxis = dict(
                showgrid = True,
                zeroline = False,
                showline = True,
                title = 'Pressure, GPa'
            ),
            yaxis=dict(
                type=self.yaxis_type,
                showgrid=True,
                zeroline=False,
                showline=True,
                title='Number of H2 molecules, %'
            ),
            hoverlabel=dict(
                namelength=-1
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

    def add_app(self, app, page):
        '''
        Here we add Dash visualisation for our data
        '''
        self.app = app
        self.callback(page)

    def callback(self, page):
        '''
        Here we explain reaction into external step change
        '''
        @self.app.callback(
            dash.dependencies.Output(self.name, 'figure'),
            [dash.dependencies.Input(page, 'pathname')])
        def update_figure(pathname):
            return self._update_graph()

    def get_html(self):
        '''
        Here we describe frontend of our object
        '''
        layout = html.Div([
            html.Div(dcc.Graph(
                id=self.name,
            ))],
            style = {'width': '100%', 'display': 'inline-block'}
        )
        return layout

    def __init__(self, common_phrase=''):
        dash_object.__init__(self)
        self.info = []
        self.common_phrase = common_phrase
        self.current_index = 0
        self.graph_type = 'scatter'
        self.name = 'Common Neighbour distribution'
        self.yaxis_type = 'linear'
        self.load_flag = 0
