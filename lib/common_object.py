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


    def _external_callback(self, step_input, value_input):
        '''
        Here we explain reaction into external step change
        '''
        @self.app.callback(
            dash.dependencies.Output(self.name, 'figure'),
            [dash.dependencies.Input(step_input, 'value')])
        def update_figure(selected_Step):
            self.current_index = self.data[self.data['Step'] == selected_Step].index[0]
            return self._update_graph()

        @self.app.callback(
            dash.dependencies.Output(self.name, 'figure'),
            [dash.dependencies.Input(value_input, 'value')])
        def update_figure(selected_Step):
            if (selected_Step in self.data['Step'].values):
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