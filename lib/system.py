from lib.load import *
import dash
import dash_core_components as dcc
import dash_html_components as html

class system(load):

    

    def set_app(self):
        self.app = dash.Dash()
        self.step_input = 'Step-slider'
        slider_step = self.steps[1] - self.steps[0]
        slider = dcc.Slider(
            id=self.step_input,
            min=self.steps[0],
            max=self.steps[-1],
            value=self.steps[0],
            step= slider_step # int number of step
            #marks={str(Step): str(Step) for Step in range(self.start, self.stop, slider_step)}
        )
        self.value_input = 'input_step'
        input = dcc.Input(
            id=self.value_input,
            placeholder='Step',
            type='value',
            value=self.steps[0]
        )



        children = []
        for object in self.objects:
            children.append( object.get_html())

        self.title = self.general_info['title']
        self.markdown = "data_file:\n{:s}\n".format(self.general_info['data_description']) 
        self.markdown += "description_file:\n{:s}".format(self.general_info['description'])

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
        
        self.app.run_server(port = self.port, host = '0.0.0.0')
        
    def __init__(self, path, objects, server = 0, minstep = 0, port = 8050, custom_steps = []):
        super(system, self).__init__(objects, minstep=minstep, custom_steps = custom_steps)
        self.port = port
        load_flag = 0
        # find backup path 
        try:
            backup_file =  glob.glob(path + '/**/**/.backup', recursive=True)[0]
        except IndexError:
            load_flag = 1
        
        if load_flag:
            self.load(path = path)
            self.upload_backup(filename = path + "/.backup")
        else:
            self.load_backup(filename = backup_file)
        '''
        if load_flag == 0:
            for object in self.objects:
                load_flag += object.load(path=backup_path)
            print ("load: {:40s}".format("checked"))

        if load_flag:
            self.load(path = path)
            for object in self.objects:
                object.save(path = backup_path)
            print("save: {:40s}".format("success"))
        else:
            self.load_step(path=lammpstrj)
        '''
        self.server = server
        self.set_app()
