# it's a common class of all system object
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import random

class dash_object:
    def load_step(self, Step, parametrs):
        '''
        Here we upload step data and put it into data structure
        '''

    def __update_graph(self):
        '''
        Here we update graph with neccessary parametrs
        :return:
        '''

    def __internal_callback(self):
        '''
        Here we explain all callback wich caused bu internal parametrs changes
        '''

    def __external_callback(self, step_input):
        '''
        Here we explain reaction into external step change
        '''

    def get_html(self):
        '''
        Here we describe frontend of our object
        '''
    def __init__(self):
        self.data = pd.DataFrame(columns=["Step", "data"])
        self.current_index = 0

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