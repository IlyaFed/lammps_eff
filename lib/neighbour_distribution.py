from lib.common_object import *
import numpy as np
import ctypes

class neighbour_distribution(dash_object):

    def _load_first_step(self, Step, coord, wall):
        self.mylib.neighbour_list.restype = ctypes.POINTER(ctypes.c_int)
        self.mylib.neighbour_list.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
            # x, y, z
            ctypes.POINTER(ctypes.c_double),  # type
            ctypes.POINTER(ctypes.c_double),  # wall
            ctypes.c_double,  # cut
            ctypes.c_int,  # n
        ]

        p_x = coord[0].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_y = coord[1].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_z = coord[2].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_type = coord[3].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_wall = wall.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        p_n = ctypes.c_int(len(coord[0]))

        p_cut = ctypes.c_double(self.cut)

        p_list = self.mylib.neighbour_list(p_x, p_y, p_z, p_type, p_wall, p_cut, p_n)
        list_dist = list(np.array(np.fromiter(p_list, dtype=np.int, count=len(coord[0]) * 2 + 7)))
        self.mylib.free_mem.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self.mylib.free_mem(p_list)
        
        types_of_every_particles = np.array(list_dist[len(coord[0]):len(coord[0])*2])
        self.data.at[Step, 'particle_type'] = types_of_every_particles

        distribution = list_dist[len(coord[0]) * 2:]
        distribution.append( len(coord[0]) - sum(distribution) ) # append "other particles"
        for i in range( len(self.particle_types)):
            self.data.at[Step, self.particle_types[i]] = distribution[i]
        

    def _load_next_step(self, Step, coord, coord_2, wall):
        self.mylib.neighbour_list_two.restype = ctypes.POINTER(ctypes.c_int)
        self.mylib.neighbour_list_two.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), # x, y, z
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), # x_2, y_2, z_2
            ctypes.POINTER(ctypes.c_double),  # type
            ctypes.POINTER(ctypes.c_double),  # wall
            ctypes.c_double,  # cut
            ctypes.c_int,  # n
        ]
        p_x = coord[0].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_y = coord[1].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_z = coord[2].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_x_2 = coord_2[0].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_y_2 = coord_2[1].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_z_2 = coord_2[2].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_type = coord_2[3].ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        p_wall = wall.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        p_n = ctypes.c_int(len(coord[0]))

        p_cut = ctypes.c_double(self.cut)

        p_list = self.mylib.neighbour_list_two(p_x, p_y, p_z, p_x_2, p_y_2, p_z_2, p_type, p_wall, p_cut, p_n)
        # print ("coord = ", coord)
        # print ("p_list = ", p_list)
        # print ("numpy = ", np.array(np.fromiter(p_list, dtype=np.int, count=len(coord[0]) * 2 + 7)))
        list_dist = list(np.array(np.fromiter(p_list, dtype=np.int, count=len(coord[0]) * 2 + 7)))
        self.mylib.free_mem.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self.mylib.free_mem(p_list)
        
        types_of_every_particles = np.array(list_dist[len(coord[0]):len(coord[0])*2])
        self.data.at[Step, 'particle_type'] = types_of_every_particles

        distribution = list_dist[len(coord[0]) * 2:]
        distribution.append( len(coord[0]) - sum(distribution) ) # append "other particles"
        for i in range( len(self.particle_types)):
            #print ("name = ", self.particle_types[i], ": ", distribution[i])
            self.data.at[Step, self.particle_types[i]] = distribution[i]
    
    def analyse(self, data, gen_info):
        self.data = data
        self.gen_info = gen_info
        n = self.gen_info['n']
        load_flag = 1
        for item in self.index_list:
            if not item in self.data.columns:
                load_flag = 0
        if load_flag:
            return 0
            
        # reserve space to particle type massives
        self.data['particle_type'] = pd.Series([np.zeros(n, dtype=float)]*self.data.shape[0])
        self.gen_info['particles_types'] = {1: 'e', 2: 'H', 3: 'H+', 4: 'H2+', 5: 'H2', 6: 'H3+', 7: 'H3', 0: 'other'}
        
        self.data['coord_neighboard'] = pd.Series([np.zeros((4,n), dtype=float)]*self.data.shape[0])

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
        our_param = parametrs[parametrs['type'] == 1.0]
        n = parametrs.shape[0]
        coord = np.zeros((4, n), dtype=float)
        for i in range(n):
            coord[0][i] = parametrs.loc[parametrs.index[i], 'x']
            coord[1][i] = parametrs.loc[parametrs.index[i], 'y']
            coord[2][i] = parametrs.loc[parametrs.index[i], 'z']
            coord[3][i] = parametrs.loc[parametrs.index[i], 'type']

        self.data.at[Step, 'coord_neighboard'] = coord
        
        #print ("type", coord[3])
        if Step == self.data.index[0]:
            #print ("first")
            self._load_first_step(Step=Step, coord=coord, wall=wall)
        else:
            previous_index = self.data.index[ list(self.data.index).index(Step) - 1] 
            coord_2 = self.data.loc[previous_index, 'coord_neighboard']
            #print( "coord = ", coord, " \ncoord_2 = ", coord_2)
            self._load_next_step(Step=Step, coord=coord, coord_2=coord_2, wall=wall)


    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []

        min_T = self.data['e'].min()
        max_T = self.data['e'].max()

        for item in self.particle_types:
            traces.append(go.Scatter(
                x = self.data.index,
                y = self.data[item].values,
                name = item,
                mode = 'line'
            ))
            min_T = min( min_T, self.data[item].min())
            max_T = max( max_T, self.data[item].max())

        step = self.current_index
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
            title = 'Neighbour distribution',
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
        self.particle_types = ["e", "H+", "H", "H2+", "H2", "H3+", "H3", "other"]
        self.index_list = self.particle_types
        self.current_index = 0
        self.graph_type = 'scatter'
        self.cut = 2.0
        self.mylib = ctypes.CDLL('lib/neighbour.so')
        self.name = 'neigbour_distribution'
