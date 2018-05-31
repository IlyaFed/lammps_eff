from lib.common_object import *
import numpy as np

class energy_distribution_electron_full(dash_object):
    def analyse(self, data, gen_info):
        self.data = data
        self.gen_info = gen_info

        load_flag = 1
        for item in self.index_list:
            if not item in self.data.columns:
                load_flag = 0
        if load_flag:
            return 0


        for item in self.index_list:
            self.data[item] = pd.Series([np.zeros((2, self.grid + 1))]*self.data.shape[0])


        parametrs = self.data.loc[self.data.index[0], 'every']
        if (not 'c_keatom' in parametrs.columns) or (not 'c_peatom' in parametrs.columns):
            logging.warning ("no {:s} in data".format(self.col_name))
            return
        for Step in self.data.index:
            self.load_step(Step)
        return 1

    def load_step(self, Step):
        parametrs = self.data.loc[Step, 'every']

        parametrs['full_energy'] =  parametrs['c_keatom'] + parametrs['c_peatom']
        self.col_name = 'full_energy'        
        '''
        Here we upload step data and put it into data structure
        '''
        
        e_hartry = 27.2113845

        energy = parametrs[parametrs['type'] == 2.0][self.col_name].apply(lambda x: x*e_hartry)
        e_max = energy.max()
        e_min = energy.min()
        e = np.zeros((2, self.grid + 1))
        if e_max != e_min:
            for i in range(self.grid + 1):
                e[0][i] = e_min + (e_max - e_min) / self.grid * i

            def f_e_dist(x):
                e[1][int((x - e_min) / (e_max - e_min) * self.grid)] += 1

            energy.apply(f_e_dist)
            
        self.data.at[Step, self.energy] = e
        

    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []
        distribution = self.data.loc[self.current_index, self.energy]
        traces.append(go.Scatter(
            x = distribution[0],
            y = distribution[1],
            name = self.energy,
            mode = 'line'
        ))

        if self.col_name == 'c_keatom':
            distribution = self.data.loc[self.current_index, 'electron_theory']
            traces.append(go.Scatter(
                x=distribution[0],
                y=distribution[1],
                name='Theory',
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
            title = 'Distribution of {:s} energy'.format(self.energy),
            xaxis = dict(
                showgrid = True,
                zeroline = False,
                showline = True,
                title = 'Energy, eV'
            ),
            yaxis=dict(
                showgrid=True,
                zeroline=False,
                showline=True,
                title='Distribution'
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
        dash_object.__init__(self)
        self.current_index = 0
        energy = "full_energy"
        self.energy = 'electron ' + energy
        self.graph_type = 'scatter'
        self.name = 'energy_distribution {:s}'.format(self.energy)
        self.grid = 100
        self.index_list = [self.energy]


