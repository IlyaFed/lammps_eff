import lib.read_lammps as rd
import lib.dash_functions as dfunc
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

class system:
    data = 0
    app = 0
    start = 0
    stop = 0
    step = 0
    m_ion = 0
    m_electron = 0
    functions = []
    items_functions = dict()
    children_little = []
    children_big = []
    style_little = {'width': '33%', 'display': 'inline-block'}
    style_big = {'width': '49%', 'display': 'inline-block'}
    layout = go.Layout(
            width = 500,
            height = 300
            )

    def read(self, fileplace, filetype):
        if filetype == 'lammpstrj':
            lammpstrj = rd.lammpstrj(start = self.start, step = self.step, stop = self.stop,  m_ion = self.m_ion, m_electron = self.m_electron)
            lammpstrj.read(path = fileplace, functions = self.functions)
            self.data = lammpstrj.data
        if filetype == 'log':
            log = rd.log()
            log.read(filename = fileplace)
            self.data = log.data

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

    def __init__(self, start, step, stop, m_ion, m_electron, functions):
        self.start = start
        self.stop = stop
        self.step = step
        self.m_ion = m_ion
        self.m_electron = m_electron
        self.functions = functions
        self.items_functions = {
                'T_i': dfunc.T_ion(self),
                'T_e': dfunc.T_electron(self),
                'X': dfunc.X_coord(self),
                'E_dist_i': dfunc.E_distribution_ion(self),
                'E_dist_e': dfunc.E_distribution_electron(self)
                }
    def set_callback(self, items):
        for item in items:
            self.items_functions[item].callback()

    def set_layout(self, items):
        for item in items:
            self.items_functions[item].layout()

        slider = dcc.Slider(
            id='Step-slider',
            min=self.data['Step'].min(),
            max=self.data['Step'].max(),
            value=self.data['Step'].min(),
            step=None,
            marks={str(Step): str(Step) for Step in self.data['Step'].values}
        )

        self.app.layout = html.Div([
            html.Div(className = 'row', children = self.children_little),
            html.Div(className = 'row', children = self.children_big),
            html.Div(children = slider, className='twelve columns'),
            ]
#            className = 'twelve columns'
            )





    def show(self, items):
        self.app = dash.Dash()

        self.set_layout(items)

        self.set_callback(items)

        self.app.run_server() #port = 8050, host = '0.0.0.')

