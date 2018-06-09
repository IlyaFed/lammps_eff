# it's a common class of all system object
from lib.common_object import *
import numpy as np


class common_neighbour_distribtution(dash_object):
    def analyse(self, system_objects):
        self.info = []
        for path in system_objects['paths']:
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

        for particle in self.particle:
            for sys_info in self.info:
                data = sys_info['data']
                geninfo = sys_info['info']
                filtrer_flag = 0
                for filtrer in self.filtrer.split(';'):
                    if filtrer in geninfo['title']: #filtrered for rho TODO
                        filtrer_flag += 1
                if filtrer_flag == 0:
                    continue
                N = data.loc[data.index[0], 'every'].shape[0]
                traces.append(go.Scatter(
                    x=data['Press'].values[1:], # GPa
                    y=data[particle].values[1:]/N*100, #[1:] - because first one is wrong
                    mode = 'line',
                    name = particle + ", " + geninfo['title']
                ))


          
        return traces

    def __get_trace(self):
        if self.graph_type == 'scatter':
            return self.__get_scatter_trace()

    def __get_layout(self):
        return go.Layout(
            showlegend = True,
            title = 'Common neighbour distribution for ' + self.filtrer,
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
            [dash.dependencies.Input(page, 'pathname'),
             dash.dependencies.Input('common_neighbour_dropdown', 'value'),
             dash.dependencies.Input('common_neighbour_filtrer_button', 'n_clicks')],
            [dash.dependencies.State('common_neighbour_filtrer', 'value')])
        def update_figure(pathname, dropdown, n_clicks, filtrer):
            if type(dropdown) is list:        
                self.particle = dropdown
            elif type(dropdown) is str:
                self.particle = [dropdown]

            if n_clicks:
                self.filtrer = filtrer
            return self._update_graph()

    def get_html(self):
        '''
        Here we describe frontend of our object
        '''
        layout = html.Div([
            dcc.Input(id='common_neighbour_filtrer', type='Filtrer (;)', value=self.filtrer, style={'width': '90%', 'height': '20pt'}),
            html.Button(id='common_neighbour_filtrer_button', n_clicks=0, children='Filtrer', style={'width': '9%'}),
            dcc.Dropdown(id='common_neighbour_dropdown',
                options=[{'label': name, 'value': name} for name in self.particle_types],
                multi=True,
                value=self.particle
            ),
            html.Div(dcc.Graph(
                id=self.name,
            ))],
            style = {'width': '100%', 'display': 'inline-block'}
        )
        return layout

    def __init__(self, filtrer=''):
        dash_object.__init__(self)
        self.info = []
        self.filtrer = filtrer
        self.current_index = 0
        self.graph_type = 'scatter'
        self.particle_types = ["e", "H+", "H", "H2+", "H2", "H3+", "H3", "H-", "other"]
        self.particle = ['H2']
        self.name = 'Common Neighbour distribution'
        self.yaxis_type = 'linear'
        self.load_flag = 0
