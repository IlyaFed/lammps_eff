# it's a common class of all system object
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import random
import os
from pathlib import Path

class dash_object:
    
    def set(self, data, gen_info):
        '''
        Here we upload step data and put it into data structure back
        '''

        self.analyse(data, gen_info)
        self.analysed_flag = 1
        return 0
        
    def is_analysed(self):
        return self.analysed_flag
    

    def load_log(self, parametrs):
        '''
        Here we get data from log lammps file
        :param Step:
        :param parametrs:
        :return:
        '''

    def analyse(self, data, gen_info):
        '''
        '''

    def update_graph(self):
        # check that data available
        if self.analysed_flag:
            return self._update_graph()
        else:
            traces = []
            layout = go.Layout(
                showlegend = False,
                width=500,
                height=300,
                title = self.name + " (not loaded)",
                xaxis = dict(
                    showgrid = True,
                    zeroline = False,
                    showline = True,
                    title = "x"
                ),
                yaxis=dict(
                    showgrid=True,
                    zeroline=False,
                    showline=True,
                    title='y'
                )
            )
            return {
                        'data': traces,
                        'layout': layout
                    }

    def _update_graph(self):
        '''
        Here we update graph with neccessary parametrs
        :return:
        '''

    def callback(self, step_input, value_input):
        '''
        Here we explain reaction into external step change
        '''
        @self.app.callback(
            dash.dependencies.Output(self.name, 'figure'),
            [dash.dependencies.Input(step_input, 'value')])
        def update_figure(selected_Step):
            #if selected_Step == 0:
            #    selected_Step = selected_Step_0
            # if not selected_Step:
            #     for arg in arguments:
            #         if arg:
            #             selected_Step = arg["points"][0]["x"]
            #             print (arg)
            #             break

            if (int(selected_Step) in self.data.index):
                self.current_index = int(selected_Step)
            return self.update_graph()

    def get_name(self):
        return self.name

    def add_app(self, app, step_input, value_input):
        '''
        Here we add Dash visualisation for our data
        '''
        self.app = app
        self.callback(step_input, value_input)

    '''
    def save(self, path="./"):
        try:
            os.stat(path)
        except:
            os.mkdir(path)
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
    '''

    def get_html(self):
        return

    def layout(self):
        '''
        Here we describe frontend of our object
        '''
        return self.get_html()
        

    def make_name_unique(self, unique_code):
        self.name = unique_code + self.name
    

    def __init__(self):
        self.analysed_flag = 0
        self.current_index = 0
        self.name = "test"