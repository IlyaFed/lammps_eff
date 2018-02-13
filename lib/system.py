from lib.load import *
import dash
import dash_core_components as dcc
import dash_html_components as html

class system(load):

    def load(self, lammpstrj, logfile):
        #self.load_lammpstrj(path = lammpstrj)
        self.load_log(name = logfile)

    def set_app(self):
        self.app = dash.Dash()
        self.step_input = 'Step-slider'
        slider_step = self.step
        slider = dcc.Slider(
            id=self.step_input,
            min=self.start,
            max=self.stop,
            value=self.start,
            step= slider_step, # int number of step
            marks={str(Step): str(Step) for Step in range(self.start, self.stop, slider_step)}
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
        
        if self.server:
            self.app.run_server(port = self.port, host = '0.0.0.0')
        else:
            self.app.run_server()

    def __init__(self, lammpstrj, logfile, objects, server = 0, minstep = 0, backup_path = "./", port = 8050):
        super(system, self).__init__(objects, minstep=minstep)
        self.port = port
        load_flag = 0
        for object in self.objects:
            load_flag += object.load(path=backup_path)
        print ("load: {:40s}".format("checked"))

        if load_flag:
            self.load(lammpstrj=lammpstrj, logfile=logfile)
            for object in self.objects:
                object.save(path = backup_path)
            print("save: {:40s}".format("success"))
        else:
            self.load_step(path=lammpstrj)
        self.server = server
        self.set_app()
