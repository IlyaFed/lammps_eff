from lib.common_object import *
import numpy as np
import ctypes

class rdf(dash_object):
    def _load_step(self, Step, coord, wall):
        self.mylib.rdf.restype = ctypes.POINTER(ctypes.c_double)
        self.mylib.rdf.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), 
            ctypes.POINTER(ctypes.c_double),
            # x, y, z, s
            ctypes.POINTER(ctypes.c_double),  # type
            ctypes.POINTER(ctypes.c_double),  # wall
            ctypes.c_int,  # n
            ctypes.c_int # grid
        ]

        p_x = coord[0].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_y = coord[1].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_z = coord[2].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_s = coord[3].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_type = coord[4].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_wall = wall.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        p_n = ctypes.c_int(len(coord[0]))

        p_grid = ctypes.c_int(self.grid)

        p_list = self.mylib.rdf(p_x, p_y, p_z, p_s, p_type, p_wall, p_n, p_grid)
        rdf_distribution = np.array(np.fromiter(p_list, dtype=np.double, count= self.grid * 3))
        self.mylib.free_mem.argtypes = [ctypes.POINTER(ctypes.c_double)]
        self.mylib.free_mem(p_list)
        
        #print ("rdf_dist, ", rdf_distribution)
        self.data.at[Step, 'rdf_radius'] = rdf_distribution[:self.grid]
        self.data.at[Step, 'rdf_ion'] = rdf_distribution[self.grid:self.grid*2]
        self.data.at[Step, 'rdf_el'] = rdf_distribution[self.grid*2:]
        
        
    def analyse(self, data, gen_info):
        self.data = data
        self.gen_info = gen_info
        load_flag = 1
        for item in self.index_list:
            if not item in self.data.columns:
                load_flag = 0
        if load_flag:
            return 0
            
        # reserve space to particle type massives
        self.data['rdf_el'] = pd.Series([np.zeros(self.grid, dtype=float)]*self.data.shape[0])
        self.data['rdf_ion'] = pd.Series([np.zeros(self.grid, dtype=float)]*self.data.shape[0])
        self.data['rdf_radius'] = pd.Series([np.zeros(self.grid, dtype=float)]*self.data.shape[0])
        for Step in self.data.index:
            self.load_step(Step)
        
        return 1

    def load_step(self, Step):
        parametrs = self.data.loc[Step, 'every']
        wall = self.data.loc[Step, 'wall']
        '''
        Here we upload step data and put it into data structure
        '''

        # read ions coordinates
        n = parametrs.shape[0]
        coord = np.zeros((5, n), dtype=float)
        for i in range(n):
            coord[0][i] = parametrs.loc[parametrs.index[i], 'x']
            coord[1][i] = parametrs.loc[parametrs.index[i], 'y']
            coord[2][i] = parametrs.loc[parametrs.index[i], 'z']
            coord[3][i] = parametrs.loc[parametrs.index[i], 'c_1a[2]']
            coord[4][i] = parametrs.loc[parametrs.index[i], 'type']

        self._load_step(Step=Step, coord=coord, wall=wall)


    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []

        traces.append(go.Scatter(
            x = self.data.loc[self.current_index, 'rdf_radius'],
            y = self.data.loc[self.current_index, 'rdf_ion'],
            name = 'ion',
            mode='line'
        ))

        traces.append(go.Scatter(
            x = self.data.loc[self.current_index, 'rdf_radius'],
            y = self.data.loc[self.current_index, 'rdf_el'],
            name = 'electron',
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
            title = 'Radial Distribution Function',
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
                title='Quantity'
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
        self.type = type
        self.index_list = ['rdf']
        self.current_index = 0
        self.graph_type = 'scatter'
        self.grid = 50
        self.mylib = ctypes.CDLL('lib/rdf_c.so')
        self.name = "rdf_distribution"
