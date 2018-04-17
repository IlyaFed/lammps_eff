# it's a common class of all system object
from lib.common_object import *
import numpy as np
from plotly import figure_factory as ff
from skimage import measure
import ctypes

class coordinate_visualisation(dash_object):
    def analyse(self, data, gen_info):
        self.data = data
        #print ("data: ", self.data)
        self.gen_info = gen_info
        # create coord_ion and coord_electron columns
        n = self.gen_info['n']
        # read ions coordinates
        load_flag = 1
        for item in self.index_list:
            if not item in self.data.columns:
                load_flag = 0
        if load_flag:
            return 0
        for item in self.index_list:
            self.data[item] = pd.Series([np.zeros((4,n), dtype=float)]*self.data.shape[0])

        for Step in self.data.index:
            self.load_step(Step)
        return 1
        
    def load_step(self, Step):
        parametrs = self.data.loc[Step, 'every']
        #print ("Step: ", Step)
        #if Step == 350000:
        #    print ("parametrs:\n", parametrs)
        wall = self.data.loc[Step, 'wall']
        '''
        Here we upload step data and put it into data structure
        '''
        our_param = parametrs[parametrs['type'] == 1.0]
        n = our_param.shape[0]
        coord_ion = np.zeros((3, n), dtype=float)
        for i in range(n):
            coord_ion[0][i] = our_param.loc[our_param.index[i], 'x']
            coord_ion[1][i] = our_param.loc[our_param.index[i], 'y']
            coord_ion[2][i] = our_param.loc[our_param.index[i], 'z']

        self.data.at[Step, 'coord_ion'] = coord_ion
        # read electron coordinates
        our_param = parametrs[parametrs['type'] == 2.0]
        n = our_param.shape[0]
        coord_electron = np.zeros((4, n), dtype=float)
        for i in range(n):
            coord_electron[0][i] = our_param.loc[our_param.index[i], 'x']
            coord_electron[1][i] = our_param.loc[our_param.index[i], 'y']
            coord_electron[2][i] = our_param.loc[our_param.index[i], 'z']
            coord_electron[3][i] = our_param.loc[our_param.index[i], 'c_1a[2]']


        self.data.at[Step, 'coord_electron'] = coord_electron

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
        
        self.data.at[Step, 'surface'] = grid


    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []
        ions = self.data.loc[self.current_index, 'coord_ion']
        traces.append(go.Scatter3d(
            x = ions[0],
            y = ions[1],
            z = ions[2],
            name = 'ions',
            mode = 'markers',
            marker = dict( size = 2)
        ))
        electrons = self.data.loc[self.current_index, 'coord_electron']
        traces.append(go.Scatter3d(
            x=electrons[0],
            y=electrons[1],
            z=electrons[2],
            name='electrons',
            mode = 'markers',
            marker = dict( size = 3)
        ))
        return traces

    def __get_types_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        if not 'coord_neighboard' in self.data.columns:
            return []
        coord_full = self.data.loc[self.current_index, 'coord_neighboard']
        types = self.gen_info['particles_types'] # real name of every type ( 1 - e, 2 - H+)
        coord_type = self.data.loc[self.current_index, 'particle_type'] # type of every partice
        n = len(coord_full[0]) # number of particles
        #print ("n = ", n)
        #print ("coord_type: ", coord_type)
        #print ("types: ", types)


        traces = []

        # add not free electrons
        coord_x = []
        coord_y = []
        coord_z = []
        for i in range(n): # TODO make it faster!
            if (not coord_type[i] == 'e') and (coord_full[3][i] == 2):
                coord_x.append(coord_full[0][i])
                coord_y.append(coord_full[1][i])
                coord_z.append(coord_full[2][i])
        
        traces.append(go.Scatter3d(
            x = coord_x,
            y = coord_y,
            z = coord_z,
            name = 'busy electron',
            mode = 'markers',
            marker = dict( size = 2)
        ))  

        for type_n in types:
            type_name = types[type_n]
            #print ("type_name" , type_name)
            coord_x = []
            coord_y = []
            coord_z = []
            for i in range(n): # TODO make it faster!
                if (coord_type[i] == type_n):
                    if type_name == 'e':
                        coord_x.append(coord_full[0][i])
                        coord_y.append(coord_full[1][i])
                        coord_z.append(coord_full[2][i])
                    elif coord_full[3][i] == 1:
                        coord_x.append(coord_full[0][i])
                        coord_y.append(coord_full[1][i])
                        coord_z.append(coord_full[2][i])
            #if len(coord_x):
            traces.append(go.Scatter3d(
                x = coord_x,
                y = coord_y,
                z = coord_z,
                name = type_name,
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
        ions = self.data.loc[self.current_index, 'coord_ion']
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
        self.isovalue_maxmin = [grid.max(), grid.min()]
        iso_value = min(self.isovalue, self.isovalue_maxmin[0] - 0.001)
        iso_value = max( iso_value, self.isovalue_maxmin[1] + 0.001)
        vertices, simplices = measure.marching_cubes_classic(self.data.loc[self.current_index, 'surface'], iso_value)
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
        item = int(self.isovalue * self.grid_N)

        if section == 'x':
            grid_new = grid[item]

        if section == 'y':
            grid_new = np.transpose(grid, (1, 2, 0))[item]

        if section == 'z':
            grid_new = np.transpose(grid, (2, 0, 1))[item]

        traces.append( go.Surface(
            z=grid_new
        ))

        '''
        ions = self.data.loc[self.current_index, 'ion']
        traces.append(go.Scatter3d(
            x=ions[0]/self.wall[0]*self.grid_N,
            y=ions[1]/self.wall[1]*self.grid_N,
            z= (grid_new.min() + grid_new.max()) * 0.5,
            name='ions',
            mode='markers',
            marker=dict(size=5)
        ))
        '''

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
        if self.graph_type == 'types':
            return self.__get_types_trace()
        

    def __get_layout(self):
        if self.graph_type == 'surface':
            layout = go.Layout(
                title = "Visualisation, isovalue from {:f} to {:f}".format(self.isovalue_maxmin[1], self.isovalue_maxmin[0])
            )
        else:
            layout = go.Layout(
                scene = dict(
                    aspectratio=dict(x=1, y=1, z=1)
                ),
                showlegend=True,
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
            self.isovalue = float(isovalue)
            self.graph_type = graph_type
            if (int(selected_Step) in self.data.index):
                self.current_index = int(selected_Step)
                #self.wall = self.data[self.data['Step'] == int(selected_Step)]['wall'].values[0]
            return self._update_graph()

    def get_html(self):
        '''
        Here we describe frontend of our object
        '''
        layout = html.Div([
            html.Div(
                dcc.RadioItems(
                    id=self.name + '_type',
                    options=[{'label': i, 'value': i} for i in ['scatter', 'surface', 'section x', 'section y', 'section z', 'types']],
                    value='types',
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
        self.current_index = 0
        self.grid_N = 50
        self.mylib = ctypes.CDLL('lib/grid_gauss.so')
        self.graph_type = 'scatter'
        self.name = 'Coordinate visualisation'
        self.isovalue = 0.01
        self.isovalue_maxmin = [0, 0]
        self.wall = [20., 20., 20.]
        self.index_list = ['coord_ion', 'coord_electron', 'coord_wall', 'surface']

