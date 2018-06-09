# it's a common class of all system object
from lib.common_object import *
import numpy as np


class common_pt_diagram(dash_object):
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

        for sys_info in self.info:
            data = sys_info['data']
            geninfo = sys_info['info']
            filtrer_flag = 0
            for filtrer in self.filtrer.split(';'):
                if filtrer in geninfo['title']: #filtrered for rho TODO
                    filtrer_flag += 1
            if filtrer_flag == 0:
                continue
            traces.append(go.Scatter(
                x=data['Press'].values, # GPa
                y=data['temp_ion'].values,
                mode = 'markers',
                name = geninfo['title']
            ))


        for item in list(self.experimental_data.keys()):
            traces.append(go.Scatter(
            x=self.experimental_data[item][1],
            y=self.experimental_data[item][0],
            mode = 'markers',
            marker={
                'symbol': "x",
                'size': 10
            },
            name = item
            ))
          
        return traces

    def __get_trace(self):
        if self.graph_type == 'scatter':
            return self.__get_scatter_trace()

    def __get_layout(self):
        return go.Layout(
            showlegend = True,
            title = 'PT diagram',
            xaxis = dict(
                showgrid = True,
                range=[0,650],
                zeroline = False,
                showline = True,
                title = 'Pressure, GPa'
            ),
            yaxis=dict(
                type=self.yaxis_type,
                range=[0,20000],
                showgrid=True,
                zeroline=False,
                showline=True,
                title='Temperature, K'
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
             dash.dependencies.Input(self.name+'yaxis_type', 'value'),
             dash.dependencies.Input('common_pt_filtrer_button', 'n_clicks')],
            [dash.dependencies.State('common_pt_filtrer', 'value')])
        def update_figure(pathname, yaxis_type, n_clicks, filtrer):
            if n_clicks:
                self.filtrer = filtrer
            #if selected_Step == 0:
            #    selected_Step = selected_Step_0
            self.yaxis_type = yaxis_type
            return self._update_graph()

    def get_html(self):
        '''
        Here we describe frontend of our object
        '''
        layout = html.Div([
            dcc.Input(id='common_pt_filtrer', type='Filtrer (;)', value=self.filtrer, style={'width': '90%', 'height': '20pt'}),
            html.Button(id='common_pt_filtrer_button', n_clicks=0, children='Filtrer', style={'width': '9%'}),
            html.Div(
                dcc.RadioItems(
                    id=self.name + 'yaxis_type',
                    options=[{'label': i, 'value': i} for i in ['linear', 'log']],
                    value='linear',
                    labelStyle={'display': 'inline-block'}
                )),
            html.Div(dcc.Graph(
                id=self.name,
            ))
            ],
            style = {'width': '100%', 'display': 'inline-block'}
        )
        return layout

    def __init__(self, experimental_data = dict()):
        dash_object.__init__(self)
        self.info = []
        self.current_index = 0
        self.graph_type = 'scatter'
        self.name = 'Common PT diagramm'
        self.filtrer = ''
        self.experimental_data = experimental_data
        self.yaxis_type = 'log'
        self.load_flag = 0
