# it's a common class of all system object
from lib.common_object import *
import numpy as np
from plotly import figure_factory as ff
from skimage import measure
import ctypes

class coordinate_visualisation(dash_object):
    def load_step(self, args):
        parametrs = args['parametrs']
        Step = args['Step']
        wall = args['wall']
        '''
        Here we upload step data and put it into data structure
        '''
        # read ions coordinates
        if self.load_flag:
            return 0
        our_param = parametrs[parametrs['type'] == 1.0]
        n = our_param.shape[0]
        coord_ion = np.zeros((3, n), dtype=float)
        for i in range(n):
            coord_ion[0][i] = our_param.loc[our_param.index[i], 'x']
            coord_ion[1][i] = our_param.loc[our_param.index[i], 'y']
            coord_ion[2][i] = our_param.loc[our_param.index[i], 'z']

        # read electron coordinates
        our_param = parametrs[parametrs['type'] == 2.0]
        n = our_param.shape[0]
        coord_electron = np.zeros((4, n), dtype=float)
        for i in range(n):
            coord_electron[0][i] = our_param.loc[our_param.index[i], 'x']
            coord_electron[1][i] = our_param.loc[our_param.index[i], 'y']
            coord_electron[2][i] = our_param.loc[our_param.index[i], 'z']
            coord_electron[3][i] = our_param.loc[our_param.index[i], 'c_1a[2]']

        self.mylib.grid_gauss.restype = ctypes.POINTER(ctypes.c_double)
        self.mylib.grid_gauss.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                     ctypes.POINTER(ctypes.c_double),
                                     ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_int,
                                     ctypes.c_int]


        p_x = coord_electron[0].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_y = coord_electron[1].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_z = coord_electron[2].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_r = coord_electron[3].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_wall = wall.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        n = ctypes.c_int(len(coord_electron[0]))
        grid_n = ctypes.c_int(self.grid_N)

        grid = self.mylib.grid_gauss(p_x, p_y, p_z, p_r, p_wall, n, grid_n)
        grid_res = np.array(np.fromiter(grid, dtype=np.float64, count=self.grid_N ** 3))
        self.mylib.free_mem.argtypes = [ctypes.POINTER(ctypes.c_double)]
        self.mylib.free_mem(grid)

        grid = np.zeros((self.grid_N, self.grid_N, self.grid_N))
        for i in range(self.grid_N):
            for j in range(self.grid_N):
                for k in range(self.grid_N):
                    grid[i][j][k] = grid_res[i * self.grid_N * self.grid_N + j * self.grid_N + k]
        self.data.loc[len(self.data)] = [Step, coord_ion, coord_electron, grid, wall]
        del grid


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
        traces = []
        ions = self.data.loc[self.current_index, 'ion']
        traces.append(go.Scatter3d(
            x=ions[0],
            y=ions[1],
            z=ions[2],
            name='ions',
            mode='markers',
            marker=dict(size=3)
        ))
        grid = self.data.loc[self.current_index, 'surface']
        wall = self.data.loc[self.current_index, 'wall']
        iso_values = self.isovalue

        self.isovalue_maxmin = [grid.min(), grid.max()]
        vertices, simplices = measure.marching_cubes_classic(self.data.loc[self.current_index, 'surface'], iso_values)
        x, y, z = zip(*vertices)
        x = np.array(x) / self.grid_N * wall[0]
        y = np.array(y) / self.grid_N * wall[1]
        z = np.array(z) / self.grid_N * wall[2]

        colormap = ['rgb(255,105,180)', 'rgb(255,105,180)', 'rgb(255,105,180)']
        traces.append( ff.create_trisurf(
            x=x,
            y=y,
            z=z,
            plot_edges=False,
            colormap=colormap,
            simplices=simplices,
            aspectratio=dict(x=1, y=1, z=1),
            title="Isosurface").data[0])
        return traces

    def __get_surface_section(self, section):
        '''
        Create surfaace graph trace
        :return:
        '''
        traces = []

        grid = self.data.loc[self.current_index, 'surface']
        #wall = self.data.loc[self.current_index, 'wall']
        if section == 'x':
            item = int( self.isovalue * grid.shape[0])
            grid = grid[item]

        if section == 'y':
            item = int( self.isovalue * grid.shape[1])
            grid = np.transpose(grid, (1, 2, 0))[item]

        if section == 'z':
            item = int( self.isovalue * grid.shape[2])
            grid = np.transpose(grid, (2, 0, 1))[item]

        colormap = ['rgb(255,105,180)', 'rgb(255,105,180)', 'rgb(255,105,180)']
        traces.append( go.Surface(
            z=grid,
            title="Surface"))
        return traces

    def __get_trace(self):
        if self.graph_type == 'scatter':
            return self.__get_scatter_trace()
        if self.graph_type == 'surface':
            return self.__get_surface_trace()
        if self.graph_type == 'section x':
            return self.__get_surface_section(section='x')
        if self.graph_type == 'section y':
            return self.__get_surface_section(section='y')
        if self.graph_type == 'section z':
            return self.__get_surface_section(section='z')

    def __get_layout(self):
        if self.graph_type == 'surface':
            layout = go.Layout(
                title = "Visualisation, isovalue from {:f} to {:f}".format(self.isovalue_maxmin[0], self.isovalue_maxmin[1])
            )
        else:
            print ("x" , self.wall)
            layout = go.Layout(
                scene = dict(
                    aspectratio=dict(x=1, y=1, z=1)
                ),
                title = "Visualisation"
            )
        return layout

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

    def _external_callback(self, step_input, value_input):
        '''
        Here we explain reaction into external step change
        '''
        @self.app.callback(
            dash.dependencies.Output(self.name, 'figure'),
            [dash.dependencies.Input(step_input, 'value'),
             dash.dependencies.Input(self.name+'_type', 'value'),
             dash.dependencies.Input(self.name+'_isovalues', 'value')])
        def update_figure(selected_Step, graph_type, isovalue):
            #if selected_Step == 0:
            #    selected_Step = selected_Step_0
            self.isovalue = isovalue
            self.graph_type = graph_type
            if (int(selected_Step) in self.data['Step'].values):
                self.current_index = self.data[self.data['Step'] == int(selected_Step)].index[0]
                self.wall = self.data[self.data['Step'] == int(selected_Step)]['wall'].values[0]
            return self._update_graph()

    def get_html(self):
        '''
        Here we describe frontend of our object
        '''
        layout = html.Div([
            html.Div(
                dcc.RadioItems(
                    id=self.name + '_type',
                    options=[{'label': i, 'value': i} for i in ['scatter', 'surface', 'section x', 'section y', 'section z']],
                    value='scatter',
                    labelStyle={'display': 'inline-block'}
                )),
            html.Div(
                dcc.Input(
                    id=self.name + '_isovalues',
                    placeholder='Value',
                    type='value',
                    value=0.5
            )),
            html.Div(dcc.Graph(
                id=self.name,
            ))],
            style={'width': '48%', 'display': 'inline-block'}
        )
        return layout

    def __init__(self):
        self.data = pd.DataFrame(columns=["Step", "ion", "electron", "surface", "wall"])
        self.current_index = 0
        self.grid_N = 50
        self.mylib = ctypes.CDLL('lib/grid_gauss.so')
        self.graph_type = 'scatter'
        self.name = 'Coordinate visualisation'
        self.isovalue = 0
        self.isovalue_maxmin = [0, 0]
        self.wall = [20., 20., 20.]


