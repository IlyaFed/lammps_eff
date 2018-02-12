# it's a common class of all system object
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

class dash_object:
    def load_step(self, parametrs):
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

    def __get_html(self):
        '''
        Here we describe frontend of our object
        '''

    def add_app(self, app, step_input):
        '''
        Here we add Dash visualisation for our data
        '''
        self.app = app
        self.__external_callback(step_input)
        self.__internal_callback()

        return self.__get_html()

    def __init__(self):
        self.data = pd.Dataframe(columns=["Step", "data"])
        self.current_index = 0


