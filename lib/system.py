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

        self.title = self.general_info['title']
        self.markdown = ""
        if self.ready_flag:
            self.markdown += "data_file:\n{:s}\n".format(self.general_info['data_description']) 
            self.markdown += "description_file:\n{:s}".format(self.general_info['description'])

        if self.back_botton:
            return html.Div([
                html.Div(id=self.unique_code),
                html.Br(),
                dcc.Link('Go back to home', href='/'),
                html.H1(self.title),
                html.Div(dcc.Markdown(self.markdown)),
                html.Div(className = 'row', children = children),
                html.Div(children = slider_element),
                html.Div(input_step_element)
                ]
                # className = 'twelve columns'
                )
        else:
            return html.Div([
                html.H1(self.title),
                html.Div(dcc.Markdown(self.markdown)),
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
