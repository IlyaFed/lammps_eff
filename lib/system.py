"""
This module create a big object which show you web page with one experimantal data
    Can be runned by threads
"""
from lib.load import load
import dash
import dash_core_components as dcc
import dash_html_components as html
#import logging
from threading import Thread

# import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from lib.glob import find_recurse


class system(load, Thread, BaseHTTPRequestHandler):
    """
    This class create a big object which show you web page with one experimantal data
    Can be runned by threads
    """

    def set_app(self, app):
        self.app = app

        # get clickData input from objects
        input_objects = []
        for object_of_system in self.objects:
            input_objects.append(dash.dependencies.Input(
                object_of_system.get_name(), 'clickData'))

        @self.app.callback(
            dash.dependencies.Output(self.step_input, 'value'),
            [dash.dependencies.Input(
                self.value_input, 'value')] + input_objects
        )
        def update_figure(selected_Step, *arguments):
            for item in arguments:
                if item:
                    selected_Step = item['points'][0]['x']
                    break
            return selected_Step

        # description
        @app.callback(
            dash.dependencies.Output(
                component_id=self.markdown_input_return, component_property='children'),
            [dash.dependencies.Input(component_id=self.data_description_input, component_property='value'),
             dash.dependencies.Input(
                 component_id=self.description_input, component_property='value'),
             dash.dependencies.Input(
                 component_id=self.title_input, component_property='value'),
             dash.dependencies.Input(component_id=self.button_input, component_property='n_clicks')]
        )
        def update_output_div(data_description, description, title, n_clicks):
            self.general_info['data_description'] = data_description
            self.general_info['description'] = description
            self.general_info['title'] = title
            if n_clicks:
                self.upload_backup(filename=self.path + "/.backup")
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

        for object_of_system in self.objects:
            object_of_system.add_app(app=self.app, step_input=self.step_input,
                                     value_input=self.value_input)

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
            step=slider_step  # int number of step
            # marks={str(Step): str(Step) for Step in range(self.start, self.stop, slider_step)}
        )

        input_step_element = dcc.Input(
            id=self.value_input,
            placeholder='Step',
            type='value',
            value=slider_min
        )
        children = []
        for object_of_system in self.objects:
            children.append(object_of_system.layout())

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
                html.Div(className='row', children=children),
                html.Div(children=slider_element),
                html.Div(input_step_element)
            ]
                # className = 'twelve columns'
            )
        else:
            return html.Div([
                html.Div(id=self.unique_code),
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
                html.Div(className='row', children=children),
                html.Div(children=slider_element),
                html.Div(input_step_element)
            ]
                # className = 'twelve columns'
            )

            # html.Div([
            #     html.H1(self.general_info['title']),
            #     html.Div(dcc.Input(id=self.markdown_input, value=self.markdown, type='text')),
            #     html.Div(id=self.markdown_input_return),
            #     #html.Div(dcc.Markdown(self.markdown)),
            #     html.Div(className = 'row', children = children),
            #     html.Div(children = slider_element),
            #     html.Div(input_step_element)
            #     ]
            #     # className = 'twelve columns'
            #     )

    def run_on_port(self, port):
        '''
        Create page of this system in this port
        '''
        self.run()
        self.back_botton = 0
        app = dash.Dash()
        app.layout = self.get_layout()
        self.set_app(app)
        self.app.run_server(port=port, host='0.0.0.0')

    def get_title(self):
        return self.general_info['title']

    def get_path(self):
        return self.path

    def info(self):
        return {
            'data': self.data,
            'info': self.general_info
        }

    def run_http(self):
        self.run()
        data_x = ' '.join([str(i) for i in self.data['Press'].values])
        data_y = ' '.join([str(i) for i in self.data['Temp'].values])

        class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

            # GET
            def do_GET(self):
                # Send response status code
                self.send_response(200)

                # Send headers
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # Send message back to client
                message = data_x + "||||" + data_y
                # Write content as utf-8 data
                self.wfile.write(bytes(message, "utf8"))
                return

        print('starting server...')

        # Server settings
        # Choose port 8080, for port 80, which is normally used for a http server, you need root access
        server_address = ('127.0.0.1', 8081)
        httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
        print('running server...')
        httpd.serve_forever()

    def is_ready(self):
        return self.ready_flag

    def run(self):
        # find backup path
        try:
            # self.backup_file =  glob.glob(self.path + '/**/**/.backup', recursive=True)[0]
            self.backup_file = find_recurse(self.path, ".backup")[0]
        except IndexError:
            self.load_flag = 1
        if self.load_flag:
            self.log("no backup file")
        else:
            self.log("backup file exist")
        if self.load_flag:
            self.load()
            self.upload_backup(filename=self.path + "/.backup")
        else:
            self.load_backup(filename=self.backup_file)
        self.ready_flag = 1

        # self.run(8050)

    def __init__(self, path, objects, minstep=0):
        Thread.__init__(self)
        load.__init__(self, objects, minstep=minstep, path=path)
        # print ("data: ", self.data)
        self.backup_file = ""
        self.path = path
        self.load_flag = 0
        self.ready_flag = 0
        self.app = 0  # todo should be dash app
        self.general_info['title'] = path.replace("./", "")
        self.back_botton = 1
        self.unique_code = path.replace('/', '').replace('.', '')

        self.step_input = self.unique_code + 'Step-slider'
        self.value_input = self.unique_code + 'input_step'
        self.description_input = self.unique_code + 'description'
        self.data_description_input = self.unique_code + 'data_description'
        self.title_input = self.unique_code + 'title'
        self.markdown_input_return = self.unique_code + 'markdown_return'
        self.button_input = self.unique_code + 'button'
        for object_of_system in self.objects:
            object_of_system.make_name_unique(self.unique_code)
