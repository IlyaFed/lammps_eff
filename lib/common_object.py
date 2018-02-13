# it's a common class of all system object
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import random
from pathlib import Path

class dash_object:
    def load_step(self, Step, parametrs):
        '''
        Here we upload step data and put it into data structure
        '''

    def load_log(self, parametrs):
        '''
        Here we get data from log lammps file
        :param Step:
        :param parametrs:
        :return:
        '''

    def _update_graph(self):
        '''
        Here we update graph with neccessary parametrs
        :return:
        '''

    def _internal_callback(self):
        '''
        Here we explain all callback wich caused bu internal parametrs changes
        '''


    def _external_callback(self, step_input):
        '''
        Here we explain reaction into external step change
        '''
        @self.app.callback(
            dash.dependencies.Output(self.name, 'figure'),
            [dash.dependencies.Input(step_input, 'value')])
        def update_figure(selected_Step):
            print (self.name, selected_Step)
            #print (self.data['Step'].values)
            self.current_index = self.data[self.data['Step'] == selected_Step].index[0]
            return self._update_graph()


    def add_app(self, app, step_input):
        '''
        Here we add Dash visualisation for our data
        '''
        self.app = app
        self._external_callback(step_input)
        self._internal_callback()

    def save(self, path="./"):
        name = path + "." + self.name + ".pkl"
        self.data.to_pickle(name)
        print ("save: {:100s}".format(self.name))

    def load(self, path="./"):
        name = path + "." + self.name + ".pkl"
        my_file = Path(name)
        if my_file.is_file():
            print("load: {:100s} yes".format(self.name))
            self.load_flag = 1
            self.data = pd.read_pickle(name)
            return 0

        print("load: {:100s} no ".format(self.name))
        self.load_flag = 0
        return 1

    def get_html(self):
        '''
        Here we describe frontend of our object
        '''
    def __init__(self):
        self.data = pd.DataFrame(columns=["Step", "data"])
        self.current_index = 0
        self.name = "test"
        self.load_flag = 1

'''
k_boltz = 1.3806485279e-23
e_harty = 4.35974417e-18
aem = 1.66e-27
ab_atu = 0.529e-10/1e-15

def E_distribution_ion(parametrs):
    def sum_func(x):
        return x['c_peatom']# + x['c_keatom']

    energy = parametrs[parametrs['type'] == 1.0].apply(sum_func, axis = 1)
    e_max = energy.max()
    e_min = energy.min()
    e = np.zeros((2, self.ion_e_dist_grid+1))
    for i in range(self.ion_e_dist_grid + 1):
        e[0][i] = e_min + (e_max - e_min) / self.ion_e_dist_grid * i

    def f_e_dist(x):
        e[1][ int(( x - e_min ) / (e_max - e_min) * self.ion_e_dist_grid) ] += 1
        pass
    energy.apply(f_e_dist)

    return e

def E_distribution_electron(parametrs):
    def sum_func(x):
        return x['c_peatom'] + x['c_keatom']

    energy = parametrs[parametrs['type'] == 2.0].apply(sum_func, axis = 1)
    e_max = energy.max()
    e_min = energy.min()
    e = np.zeros((2, self.el_e_dist_grid+1))
    for i in range(self.el_e_dist_grid+1):
        e[0][i] = e_min + (e_max - e_min) / self.el_e_dist_grid * i

    def f_e_dist(x):
        e[1][ int(( x - e_min ) / (e_max - e_min) * self.el_e_dist_grid) ] += 1
        pass
    energy.apply(f_e_dist)

    return e

   def make_2D(self, item, columns):
        @self.app.callback(
            dash.dependencies.Output(item, 'figure'),
            [dash.dependencies.Input('Step-slider', 'value')])

        def update_figure(selected_Step):
            filtered_df = self.data[self.data['Step'] == selected_Step]
            traces = []
            for col in columns:
                buf_data = filtered_df[col].values[0]
                traces.append( go.Scatter(
                    x = buf_data[0],
                    y = buf_data[1],
                    mode = 'line'
                ))

            return {
                    'data': traces,
                    'layout': self.layout
                    }

    def make_1D(self, item, columns):

        @self.app.callback(
            dash.dependencies.Output(item, 'figure'),
            [dash.dependencies.Input('Step-slider', 'value')])

        def update_figure(selected_Step):
            traces = []
            for col in columns:
                traces.append( go.Scatter(
                    x = self.data['Step'].values,
                    y = self.data[col].values,
                    mode = 'line'
                ))

                extra_data = self.data[self.data['Step'] == selected_Step][col].values[0]
                traces.append( go.Scatter(
                    x = [selected_Step],
                    y = [extra_data],
                    mode = 'markers',
                    marker = dict( size = 8 )
                ))


            return {
                    'data': traces,
                    'layout': self.layout
                    }
'''
