from lib.load import *
import dash
import dash_core_components as dcc
import dash_html_components as html

class system(load):

    def load(self, fileplace, filetype):
        if filetype == 'lammpstrj':
            self.load_lammpstrj(path = fileplace)
        if filetype == 'log':
            self.load_log(name = fileplace)

    def set_app(self):
        self.app = dash.Dash()
        self.step_input = 'Step-slider'

        slider = dcc.Slider(
            id=self.step_input,
            min=self.start,
            max=self.stop,
            value=self.start,
            step=None,
            marks={str(Step): str(Step) for Step in range(self.start, self.stop, self.step)}
        )

        children = []
        for object in self.objects:
            children.append( object.get_html())


        self.app.layout = html.Div([
            html.Div(className = 'row', children = children),
            html.Div(children = slider),
            ]
            # className = 'twelve columns'
            )
        for object in self.objects:
            object.add_app(app = self.app, step_input = self.step_input)

        self.app.run_server()

    def __init__(self, fileplace, objects, filetype = ''):
        if filetype == '':
            try:
                filetype = fileplace.split('.')[-1]
            except:
                print ("error: need filetype")
                exit(1)
        super(system, self).__init__(objects)
        self.load(fileplace=fileplace, filetype=filetype)
        self.set_app()