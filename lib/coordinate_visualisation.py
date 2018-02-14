# it's a common class of all system object
from lib.common_object import *
import numpy as np

class coordinate_visualisation(dash_object):
    def load_step(self, Step, parametrs):

        '''
        Here we upload step data and put it into data structure
        '''
        # read ions coordinates
        if self.load_flag:
            return 0
        our_param = parametrs[parametrs['type'] == 1.0]
        n = our_param.shape[0]
        coord_ion = np.zeros((3, n))
        for i in range(n):
            coord_ion[0][i] = our_param.loc[our_param.index[i], 'x']
            coord_ion[1][i] = our_param.loc[our_param.index[i], 'y']
            coord_ion[2][i] = our_param.loc[our_param.index[i], 'z']

        # read electron coordinates
        our_param = parametrs[parametrs['type'] == 2.0]
        n = our_param.shape[0]
        coord_electron = np.zeros((4, n))
        for i in range(n):
            coord_electron[0][i] = our_param.loc[our_param.index[i], 'x']
            coord_electron[1][i] = our_param.loc[our_param.index[i], 'y']
            coord_electron[2][i] = our_param.loc[our_param.index[i], 'z']
            coord_electron[3][i] = our_param.loc[our_param.index[i], 'c_1a[2]']
        self.data.loc[len(self.data)] = [Step, coord_ion, coord_electron]

    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []
        ions = self.data.loc[self.current_index, 'ion']
        traces.append(go.Scatter3d(
            x = ions[0],
            y = ions[1],
            z = ions[2],
            name = 'ions',
            mode = 'markers',
            marker = dict( size = 2)
        ))
        electrons = self.data.loc[self.current_index, 'electron']
        traces.append(go.Scatter3d(
            x=electrons[0],
            y=electrons[1],
            z=electrons[2],
            name='electronss',
            mode = 'markers',
            marker = dict( size = 3)
        ))
        return traces

    def __get_surface_trace(self):
        '''
        Create surfaace graph trace
        :return:
        '''

    def __get_trace(self):
        if self.graph_type == 'scatter':
            return self.__get_scatter_trace()
        if self.graph_type == 'surface':
            return self.__get_surface_trace()

    def _update_graph(self):
        '''
        Here we update graph with neccessary parametrs
        :return:
        '''
        traces = self.__get_trace()

        return {
            'data': traces,
            'layout': go.Layout()
        }

    def _internal_callback(self):
        '''
        Here we explain all callback which caused bu internal parametrs changes
        '''

    def _external_callback(self, step_input, value_input):
        '''
        Here we explain reaction into external step change
        '''
        @self.app.callback(
            dash.dependencies.Output(self.name, 'figure'),
            [dash.dependencies.Input(step_input, 'value'),
             dash.dependencies.Input(self.name+'_type', 'value')])
        def update_figure(selected_Step, graph_type):
            #if selected_Step == 0:
            #    selected_Step = selected_Step_0
            self.graph_type = "scatter" #TODO
            if (int(selected_Step) in self.data['Step'].values):
                self.current_index = self.data[self.data['Step'] == int(selected_Step)].index[0]
            return self._update_graph()

    def get_html(self):
        '''
        Here we describe frontend of our object
        '''
        layout = html.Div([
            html.Div(
                dcc.RadioItems(
                    id=self.name + '_type',
                    options=[{'label': i, 'value': i} for i in ['scatter', 'scale']],
                    value='linear',
                    labelStyle={'display': 'inline-block'}
                )),
            html.Div(dcc.Graph(
                id=self.name,
            ))],
            style={'width': '48%', 'display': 'inline-block'}
        )
        return layout

    def __init__(self):
        self.data = pd.DataFrame(columns=["Step", "ion", "electron"])
        self.current_index = 0
        self.graph_type = 'scatter'
        self.name = 'Coordinate visualisation'


