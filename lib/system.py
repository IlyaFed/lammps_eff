from lib.load import *
import dash
import dash_core_components as dcc
import dash_html_components as html
import logging
from threading import Thread


class system(load, Thread):

    def set_app(self, app):
        self.app = app
        

        @self.app.callback(
            dash.dependencies.Output(self.step_input, 'value'),
            [dash.dependencies.Input(self.value_input, 'value')]
        )
        def update_figure(selected_Step):
            return selected_Step

        #description
        @app.callback(
            dash.dependencies.Output(component_id=self.markdown_input_return, component_property='children'),
            [dash.dependencies.Input(component_id=self.data_description_input, component_property='value'),
            dash.dependencies.Input(component_id=self.description_input, component_property='value'),
            dash.dependencies.Input(component_id=self.title_input, component_property='value'),
            dash.dependencies.Input(component_id=self.button_input, component_property='n_clicks')]
        )
        def update_output_div(data_description, description, title, n_clicks):
            self.general_info['data_description'] = data_description
            self.general_info['description'] = description
            self.general_info['title'] = title
            if n_clicks:
                self.upload_backup(filename = self.path + "/.backup")
                return "saved"
            return "success"

        # @app.callback(
        #     dash.dependencies.Output(component_id=self.markdown_input_return, component_property='children'),
        #     [dash.dependencies.Input(component_id=self.button_input, component_property='n_clicks')]
        # )
        # def update_output_div(n_clicks):
            
        #     return "saved"

        # @self.app.callback(
        #     dash.dependencies.Output(self.value_input, 'value'),
        #     [dash.dependencies.Input(self.step_input, 'value')])
        # def update_figure_2(selected_Step):
        #     return selected_Step

        for object in self.objects:
            object.add_app(app = self.app, step_input = self.step_input, value_input=self.value_input)
                

    def get_layout(self):
        

        slider_step = 0
        slider_min = 0
        slider_max = 0
        if self.ready_flag:
            slider_step = self.data.index[1] - self.data.index[0]
            slider_min = self.data.index[0]
            slider_max = self.data.index[-1]
            
        slider_element = dcc.Slider(
            id=self.step_input,
            min=slider_min,
            max=slider_max,
            value=slider_min,
            step= slider_step # int number of step
            #marks={str(Step): str(Step) for Step in range(self.start, self.stop, slider_step)}
        )

        input_step_element = dcc.Input(
            id=self.value_input,
            placeholder='Step',
            type='value',
            value=slider_min
        )        
        children = []
        for object in self.objects:
            children.append( object.layout())

        if self.back_botton:
            return html.Div([
                html.Div(id=self.unique_code),
                html.Br(),
                dcc.Link('Go back to home', href='/'),
                html.H1(self.general_info['title']),
                dcc.Textarea(
                    id=self.data_description_input,
                    title="Input data description",
                    value=self.general_info['data_description'],
                    style={
                        'width': '100%',
                        'height': '40pt'
                        }
                ),
                dcc.Textarea(
                    id=self.description_input,
                    title="Description",
                    value=self.general_info['description'],
                    style={
                        'width': '100%',
                        'height': '100pt'
                    }
                ),
                dcc.Textarea(
                    id=self.title_input,
                    title="Title",
                    value=self.general_info['title'],
                    style={
                        'width': '100%',
                        'height': '10pt'
                        }
                ),
                html.Button('Save', id=self.button_input),
                html.Div(id=self.markdown_input_return),
                html.Div(className = 'row', children = children),
                html.Div(children = slider_element),
                html.Div(input_step_element)
                ]
                # className = 'twelve columns'
                )
        else:
            return html.Div([
                html.H1(self.title),
                html.Div(dcc.Input(id=self.markdown_input, value=self.markdown, type='text')),
                html.Div(id=self.markdown_input_return),
                #html.Div(dcc.Markdown(self.markdown)),
                html.Div(className = 'row', children = children),
                html.Div(children = slider_element),
                html.Div(input_step_element)
                ]
                # className = 'twelve columns'
                )

    def run_on_port(self, port):
        '''
        Create page of this system in this port
        '''
        self.run()
        self.back_botton = 0
        app = dash.Dash()
        app.layout = self.get_layout()
        self.set_app(app)
        self.app.run_server(port = port, host = '0.0.0.0')

    def get_title(self):
        return self.general_info['title']

    # def load_everything(self, path):
    #     class load_thread(Thread):
    #         def __init__(self, path):
    #             Thread.__init__(self)
    #             self.path = path
                
        
    #     my_thread = load_thread(path)
    #     my_thread.start()


    def __init__(self, path, objects, minstep = 0, custom_steps = []):
        Thread.__init__(self)
        logging.basicConfig(filename="log.log", level=logging.INFO)
        load.__init__(self, objects, minstep=minstep, custom_steps = custom_steps, path = path)
        #print ("data: ", self.data)
        self.path = path
        self.load_flag = 0
        self.ready_flag = 0
        self.general_info['title'] = path.replace("./","")
        self.back_botton = 1
        self.unique_code = path.replace('/','').replace('.','')
         
        self.step_input = self.unique_code + 'Step-slider'
        self.value_input = self.unique_code + 'input_step'
        self.description_input = self.unique_code + 'description'
        self.data_description_input = self.unique_code + 'data_description'
        self.title_input = self.unique_code + 'title'
        self.markdown_input_return = self.unique_code + 'markdown_return'
        self.button_input = self.unique_code + 'button'
        for object in self.objects:
            object.make_name_unique(self.unique_code)
    
    def info(self):
        return {
            'data': self.data,
            'info': self.general_info
        }

    def is_ready(self):
        return self.ready_flag

    def run(self):
        # find backup path 
        try:
            self.backup_file =  glob.glob(self.path + '/**/**/.backup', recursive=True)[0]
        except IndexError:
            self.load_flag = 1
        if self.load_flag:
            logging.info("no backup file")
        else:
            logging.info("backup file exist")
        if self.load_flag:
            self.load()
            self.upload_backup(filename = self.path + "/.backup")
        else:
            self.load_backup(filename = self.backup_file)
        self.ready_flag = 1

        #self.run(8050)
