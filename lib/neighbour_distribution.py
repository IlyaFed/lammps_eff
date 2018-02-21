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

        distribution = list_dist[len(coord[0]) * 2:]
        self.data.loc[len(self.data)] = [Step, coord, wall] + distribution

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

        distribution = list_dist[len(coord[0]) * 2:]
        self.data.loc[len(self.data)] = [Step, coord, wall] + distribution


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
        n = parametrs.shape[0]
        coord = np.zeros((4, n), dtype=float)
        for i in range(n):
            coord[0][i] = parametrs.loc[parametrs.index[i], 'x']
            coord[1][i] = parametrs.loc[parametrs.index[i], 'y']
            coord[2][i] = parametrs.loc[parametrs.index[i], 'z']
            coord[3][i] = parametrs.loc[parametrs.index[i], 'type']

        #print ("type", coord[3])
        if self.data.shape[0] < 3:
            #print ("first")
            self._load_first_step(Step=Step, coord=coord, wall=wall)
        else:
            coord_2 = self.data.loc[self.data.index[-3], 'coord']
            self._load_next_step(Step=Step, coord=coord, coord_2=coord_2, wall=wall)


    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []

        min_T = self.data['e'].min()
        max_T = self.data['e'].max()

        for item in self.data_items:
            traces.append(go.Scatter(
                x = self.data['Step'].values,
                y = self.data[item].values,
                name = item,
                mode = 'line'
            ))
            min_T = min( min_T, self.data[item].min())
            max_T = max( max_T, self.data[item].max())

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
        self.data = pd.DataFrame(columns=["Step", "coord", "wall", "e", "H+", "H", "H2+", "H2", "H3+", "H3"])
        self.data_items = self.data.columns[3:]
        self.current_index = 0
        self.graph_type = 'scatter'
        self.cut = 1.0
        self.mylib = ctypes.CDLL('lib/neighbour.so')
        self.name = 'neigbour_distribution'
