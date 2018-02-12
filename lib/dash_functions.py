import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
  #  Maxwell_ion = [E**0.5*np.exp(-3*E/2/T_ion)
class T_electron:
    def __init__(self, obj):
        self.obj= obj

    def layout(self):
        self.obj.children_little.append(
            html.Div(
                dcc.Graph(
                    id='T_e',
                    ),
                style = self.obj.style_little
                )
        )

    def callback(self):
        self.obj.make_1D('T_e', ['T_e'])

class T_ion:
    def __init__(self, obj):
        self.obj= obj
    def layout(self):
        self.obj.children_little.append(
            html.Div(
                dcc.Graph(
                    id='T_i',
                    ),
                style = self.obj.style_little
                )
            )

    def callback(self):
        self.obj.make_1D('T_i', ['T_i'])

class E_distribution_ion:
    def __init__(self, obj):
        self.obj = obj

    def layout(self):
        self.obj.children_little.append(
                html.Div(
                    dcc.Graph(
                        id='E_dist_i',
                        ),
                    style = self.obj.style_little
                    )
                )

    def callback(self):
        self.obj.make_2D('E_dist_i', ['E_dist_i'])

class E_distribution_electron:
    def __init__(self, obj):
        self.obj = obj

    def layout(self):
        self.obj.children_little.append(
                html.Div(
                    dcc.Graph(
                        id='E_dist_e',
                        ),
                    style = self.obj.style_little
                    )
                )

    def callback(self):
        self.obj.make_2D('E_dist_e', ['E_dist_e'])

class X_coord:

    def __init__(self, obj):
        self.obj= obj
        self.item = 'X'
        self.mol_types = ['ion', 'electron']

    def layout(self):
        self.obj.children_big.append(
                html.Div(
                    dcc.Graph(
                        id=self.item,
                        ),
                    style = self.obj.style_big
                    )
                )
    def callback(self):
        @self.obj.app.callback(
            dash.dependencies.Output(self.item, 'figure'),
            [dash.dependencies.Input('Step-slider', 'value')])

        def update_figure(selected_Step):
            our_data = self.obj.data[self.obj.data['Step'] == selected_Step][self.item].values[0]
            traces = []
            for types_index in range(len(our_data)):
                filtered_data = our_data[types_index]
                traces.append( go.Scatter3d(
                    x = filtered_data[0],
                    y = filtered_data[1],
                    z = filtered_data[2],
                    mode = 'markers',
                    name = self.mol_types[types_index],
                    marker = dict( size = 5 )
                    ))

            return {
                'data': traces,
                'layout': go.Layout()
                }


