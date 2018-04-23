from lib.load import *
import dash
import dash_core_components as dcc
import dash_html_components as html
import logging

class system(load):

    def set_app(self, app):
        self.app = app
        

        @self.app.callback(
            dash.dependencies.Output(self.step_input, 'value'),
            [dash.dependencies.Input(self.value_input, 'value')]
        )
        def update_figure(selected_Step):
            return selected_Step

        # @self.app.callback(
        #     dash.dependencies.Output(self.value_input, 'value'),
        #     [dash.dependencies.Input(self.step_input, 'value')])
        # def update_figure_2(selected_Step):
        #     return selected_Step

        for object in self.objects:
            object.add_app(app = self.app, step_input = self.step_input, value_input=self.value_input)
        
    def get_layout(self):
        slider_step = self.data.index[1] - self.data.index[0]
        slider = dcc.Slider(
            id=self.step_input,
            min=self.data.index[0],
            max=self.data.index[-1],
            value=self.data.index[0],
            step= slider_step # int number of step
            #marks={str(Step): str(Step) for Step in range(self.start, self.stop, slider_step)}
        )
        input = dcc.Input(
            id=self.value_input,
            placeholder='Step',
            type='value',
            value=self.data.index[0]
        )        
        children = []
        for object in self.objects:
            children.append( object.get_html())

        self.title = self.general_info['title']
        self.markdown = "data_file:\n{:s}\n".format(self.general_info['data_description']) 
        self.markdown += "description_file:\n{:s}".format(self.general_info['description'])

        if self.back_botton:
            return html.Div([
                html.H1(self.title),
                html.Div(dcc.Markdown(self.markdown)),
                html.Div(className = 'row', children = children),
                html.Div(children = slider),
                html.Div(input),
                html.Div(id='page-1-content'),
                html.Br(),
                dcc.Link('Go back to home', href='/')
                ]
                # className = 'twelve columns'
                )
        else:
            return html.Div([
                html.H1(self.title),
                html.Div(dcc.Markdown(self.markdown)),
                html.Div(className = 'row', children = children),
                html.Div(children = slider),
                html.Div(input)
                ]
                # className = 'twelve columns'
                )

    def run(self, port):
        self.back_botton = 1
        app = dash.Dash()
        app.layout = self.get_layout()
        self.set_app(app)
        self.app.run_server(port = port, host = '0.0.0.0')

    def get_title(self):
        return self.general_info['title']

    def __init__(self, path, objects, minstep = 0, custom_steps = []):
        logging.basicConfig(filename="log.log", level=logging.INFO)
        super(system, self).__init__(objects, minstep=minstep, custom_steps = custom_steps, path = path)
        load_flag = 0
        # find backup path 
        try:
            backup_file =  glob.glob(path + '/**/**/.backup', recursive=True)[0]
        except IndexError:
            load_flag = 1
        
        if load_flag:
            self.load()
            self.upload_backup(filename = path + "/.backup")
        else:
            self.load_backup(filename = backup_file)

        self.back_botton = 0
        self.unique_code = path.replace('/','')
        self.step_input = self.unique_code + 'Step-slider'
        self.value_input = self.unique_code + 'input_step'
        for object in self.objects:
            object.make_name_unique(self.unique_code)



        #self.run(8050)
