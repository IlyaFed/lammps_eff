from lib.common_object import *
import numpy as np

class energy_distribution_electron(dash_object):
    def load_step(self, Step, parametrs):
        '''
        Here we upload step data and put it into data structure
        '''

        grid = 100
        e_hartry = 27.2113845

        if self.energy == 'potential':
            col_name = 'c_peatom'
        else:
            col_name = 'c_keatom'

        energy = parametrs[parametrs['type'] == 2.0][col_name].apply(lambda x: x*e_hartry)
        e_max = energy.max()
        e_min = energy.min()
        e = np.zeros((2, grid + 1))
        for i in range(grid + 1):
            e[0][i] = e_min + (e_max - e_min) / grid * i

        def f_e_dist(x):
            e[1][int((x - e_min) / (e_max - e_min) * grid)] += 1

        energy.apply(f_e_dist)
        '''
        Temperature = 2. / 3. / (parametrs[parametrs['type'] == 1.0]['c_keatom'].mean() * e_hartry)
        if self.energy == 'potential':
            theory = e.copy()
            for i in range(grid + 1):
                theory[1][i] = np.exp(- theory[0][i] / Temperature )

            theory[1] = theory[1] / sum(theory[1]) * sum(e[1])
        else:
            theory = e.copy()
            for i in range(grid + 1):
                theory[1][i] = theory[0][i] ** 0.5 * np.exp(- theory[0][i] / Temperature)

            theory[1] = theory[1] / sum(theory[1]) * sum(e[1])
        '''
        self.data.loc[len(self.data)] = [Step, e]

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

        return traces

    def __get_trace(self):
        if self.graph_type == 'scatter':
            return self.__get_scatter_trace()

    def __get_layout(self):
        return go.Layout(
            showlegend = True,
            width=500,
            height=300,
            title = 'Distribution of {:s} electron energy'.format(self.energy),
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
    def __update_graph(self):
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

    def __internal_callback(self):
        '''
        Here we explain all callback which caused bu internal parametrs changes
        '''


    def __external_callback(self, step_input):
        '''
        Here we explain reaction into external step change
        '''
        @self.app.callback(
            dash.dependencies.Output(self.name, 'figure'),
            [dash.dependencies.Input(step_input, 'value')])
        def update_figure(selected_Step):
            self.current_index = self.data[self.data['Step'] == selected_Step].index[0]
            return self.__update_graph()



    def add_app(self, app, step_input):
        '''
        Here we add Dash visualisation for our data
        '''
        self.app = app
        self.__external_callback(step_input)
        self.__internal_callback()

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

    def __init__(self, energy):
        self.data = pd.DataFrame(columns=["Step", energy])
        self.current_index = 0
        self.energy = energy
        self.graph_type = 'scatter'
        self.name = 'energy_distribution_electron' + str(random.randrange(200)) # it's for not one graph


