# it's a common class of all system object
from lib.common_object import *
import numpy as np


class temperature(dash_object):
    def load_step(self, Step, parametrs):
        '''
        Here we upload step data and put it into data structure
        '''
        if self.load_flag:
            return 0
        k_boltz = 1.3806485279e-23
        e_harty = 4.35974417e-18
        # read ions temp
        our_param = parametrs[parametrs['type'] == 1.0]
        ion = 2. / 3. / k_boltz *  (our_param['c_keatom'].mean() * e_harty)
        # read electron temp
        our_param = parametrs[parametrs['type'] == 2.0]
        electron = 2. / 4. / k_boltz * (our_param['c_keatom'].mean() * e_harty)
        self.data.loc[len(self.data)] = [Step, ion, electron]

    def __get_scatter_trace(self):
        '''
        Here we create scatter trace for graph
        :return:
        '''
        traces = []

        traces.append(go.Scatter(
            x = self.data['Step'].values,
            y = self.data['ion'].values,
            name = 'ions',
            mode = 'line'
        ))
        traces.append(go.Scatter(
            x=self.data['Step'].values,
            y=self.data['electron'].values,
            name='electrons',
            mode = 'line'
        ))
        # create line in choosen step
        max_T = max(self.data['ion'].max(), self.data['electron'].max())
        min_T = min(self.data['ion'].min(), self.data['electron'].min())
        step = self.data.loc[self.current_index, 'Step']
        traces.append(go.Scatter(
            x = np.linspace(step, step, 100),
            y = np.linspace(min_T, max_T, 100),
            name = 'current step'
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
            title = 'Temperature of system',
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
                title='Temperature, K'
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
        ''''
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
        self.data = pd.DataFrame(columns=["Step", "ion", "electron"])
        self.current_index = 0
        self.graph_type = 'scatter'
        self.name = 'temperature'


'''
def T_electron_slow(parametrs):
    our_param = parametrs[parametrs['type'] == 2.0]
    def f_T_electron(param):
        v2 = param['vx']**2 + param['vy']**2 + param['vz']**2
        rad_v2 = param['c_1a[3]']**2
        return v2 + 0.75 * rad_v2
    v2_mean = our_param.apply(f_T_electron, axis=1).mean()
    return 2. / 4. / self.k_boltz * (self.m_electron * self.aem) / 2 * (self.ab_atu**2 * v2_mean)

def T_ion_slow(parametrs):
    our_param = parametrs[parametrs['type'] == 1.0]
    def f_T_ion(param):
        v2 = param['vx']**2 + param['vy']**2 + param['vz']**2
        return v2
    v2_mean = our_param.apply(f_T_ion, axis=1).mean()
    return 2. / 3. / self.k_boltz * (self.m_ion * self.aem) / 2 * (self.ab_atu**2 * v2_mean)

'''