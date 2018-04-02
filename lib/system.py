from lib.load import *
import dash
import dash_core_components as dcc
import dash_html_components as html

class system(load):

    def load(self, lammpstrj, logfile):
        self.load_lammpstrj(path = lammpstrj)
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
            step= slider_step # int number of step
            #marks={str(Step): str(Step) for Step in range(self.start, self.stop, slider_step)}
        )
        self.value_input = 'input_step'
        input = dcc.Input(
            id=self.value_input,
            placeholder='Step',
            type='value',
            value=self.start
        )



        children = []
        for object in self.objects:
            children.append( object.get_html())


        self.app.layout = html.Div([
            html.H1(self.title),
            html.Div(dcc.Markdown(self.markdown)),
            html.Div(className = 'row', children = children),
            html.Div(children = slider),
            html.Div(input)
            ]
            # className = 'twelve columns'
            )

        @self.app.callback(
            dash.dependencies.Output(self.step_input, 'value'),
            [dash.dependencies.Input(self.value_input, 'value')])
        def update_figure(selected_Step):
            return selected_Step

        # @self.app.callback(
        #     dash.dependencies.Output(self.value_input, 'value'),
        #     [dash.dependencies.Input(self.step_input, 'value')])
        # def update_figure_2(selected_Step):
        #     return selected_Step

        for object in self.objects:
            object.add_app(app = self.app, step_input = self.step_input, value_input=self.value_input)
        
        if self.server:
            self.app.run_server(port = self.port, host = '0.0.0.0')
        else:
            self.app.run_server()

    def __init__(self, lammpstrj, logfile, objects, server = 0, minstep = 0, backup_path = "./", port = 8050,
                 markdown="", title='', custom_steps = []):
        super(system, self).__init__(objects, minstep=minstep, custom_steps = custom_steps)
        self.title = title
        self.markdown = markdown
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
