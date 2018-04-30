from lib.system import system

from lib.coordinate_visualisation import coordinate_visualisation
from lib.temperature import temperature
from lib.pressure import pressure
from lib.energy_distribution_ion import energy_distribution_ion
from lib.energy_distribution_electron import energy_distribution_electron
from lib.energy import energy
from lib.neighbour_distribution import neighbour_distribution
from lib.pt_diagram import pt_diagram
from lib.rdf import rdf

from lib.common_pt_diagram import common_pt_diagram

import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html

VALID_USERNAME_PASSWORD_PAIRS = [
    ['hydrogen', 'hydrogen']
]
PORT = 8050
import logging
logging.basicConfig(filename="log.log", level=logging.INFO)

experimental_data = {
    'Knudson': [[900, 1250, 1600, 1700], [310, 290, 285, 285]],
    'Loubeyre': [[2000, 3000, 350, 350], [110, 50, 40, 25]],
    'Ohta': [[1750, 2200], [105, 85]],
    'Silvera': [[1100, 1300, 1400, 1600, 1750], [160, 150, 140, 120, 110]]
}

def read_paths(filename):
    with open(filename, "r") as file:
        paths = [line.replace("\n","") for line in  file.readlines()]
    return paths

def run_systems(paths):
    '''
    Run system objects in parallel
    return: dictionary of systems
    '''
    global experimental_data
    system_objects = dict()
    for path in paths:
        objects = [coordinate_visualisation(),
                    pt_diagram(experimental_data),
                    temperature(),
                    pressure(),
                    energy_distribution_ion('potential'), energy_distribution_ion('kinetic'),
                    energy_distribution_electron('potential'), energy_distribution_electron('kinetic'),
                    energy(),
                    neighbour_distribution(),
                    rdf()]
        #system_objects
        system_objects[path] = system(path = path, objects = objects)
        system_objects[path].start()
    return system_objects
 

def set_app():
    global VALID_USERNAME_PASSWORD_PAIRS
    app = dash.Dash('auth')
    auth = dash_auth.BasicAuth(
        app,
        VALID_USERNAME_PASSWORD_PAIRS
    )
    app.config.suppress_callback_exceptions = True # allow callback for non-existence id
    return app

def get_main_layout(common_pt):
    return html.Div([
    # represents the URL bar, doesn't render anything
    html.H1("Hydrogen observation"),
    html.Div(common_pt.layout()),
    dcc.Location(id='url', refresh=False),
    # content will be rendered in this element
    html.Div(id='page-content')]
    )


def set_objects_app(app, system_objects):
    for path in system_objects:
        system_objects[path].set_app(app)

def get_layout_list(system_objects):
    '''
    Get and update list of titles
    return: layout list of title html-structure
    '''
    layout_list = []
    for path in system_objects:
        #if not path in system_objects:
        #    continue # this work is not finished, should wait
        title = system_objects[path].get_title()
        
        layout_list.append( dcc.Link(title, href="/" + path) )
        layout_list.append( html.Br())
    return layout_list

if __name__ == "__main__":
    app = set_app()

    paths = read_paths("input.txt")
    system_objects = run_systems(paths)
    common_pt = common_pt_diagram(experimental_data)
    common_pt.analyse(system_objects)
    common_pt.add_app(app, page='url')
    app.layout = get_main_layout(common_pt)
    set_objects_app(app, system_objects)
    
    @app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
    def display_page(pathname):
        common_pt.analyse(system_objects)
        if not pathname:
            return html.Div(get_layout_list(system_objects))
        
        pathname_real = pathname[1:] # remove '/'
        if pathname_real in system_objects:
            return system_objects[pathname_real].get_layout()
        else:
            return html.Div(get_layout_list(system_objects))

    app.css.append_css({
        'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
    })

    app.run_server(port = PORT, host = '0.0.0.0')

