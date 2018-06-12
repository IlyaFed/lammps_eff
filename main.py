from lib.system import system

from lib.coordinate_visualisation import coordinate_visualisation
from lib.temperature import temperature
from lib.pressure import pressure
from lib.energy_distribution_ion import energy_distribution_ion
from lib.energy_distribution_electron import energy_distribution_electron
from lib.energy_distribution_electron_full import energy_distribution_electron_full
from lib.energy import energy
from lib.neighbour_distribution import neighbour_distribution
from lib.pt_diagram import pt_diagram
from lib.rdf import rdf

from lib.common_pt_diagram import common_pt_diagram
from lib.common_neighbour_distribution import common_neighbour_distribtution

import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html

#import markdown
VALID_USERNAME_PASSWORD_PAIRS = [
    ['hydrogen', 'hydrogen']
    ]
PORT = 8050
COMMON_PHRASE_FOR_NEIGHBOUR='rho0.6;rho=0.6'

import logging
logging.basicConfig(filename="log.log", level=logging.INFO)

experimental_data = {
    'Kopyshev, 1980': [[3861.82, 4127.30], [126.64, 150.56], 'markers'],
    'Weir, 1996(99)': [[2615], [139], 'markers'],
    'Loubeyre, 2004': [[4201, 4866, 4693], [49, 45, 21], 'markers'],
    'Gryaznov, 2004': [[2616, 2498], [151, 127], 'markers'],
    'Silvera, 2013': [[1584.29, 1567.11, 1648.34],[160.95, 130.70, 125.28], 'markers'],
    'Silvera, 2015': [[171.33, 160.50, 152.37, 134.31, 131.15, 122.57, 113.09], 
                      [1105.84, 1353.96, 1424.04, 1734.42, 1998.67, 1598.87, 1733.49], 'markers'],
    'Ohta, 2015': [[106.32, 92.33, 85.10, 85.55, 82.39], 
                   [1759.74, 2165.34, 2254.52, 2395.89, 2395.70], 'markers'],
    'Tablyn, 2015': [[1575, 1771], [127, 151], 'markers'],
    'Melt line': [[12.203598522461107, 93.57747150176783, 174.94141478333404, 260.8333002343411, 
                   382.88914485443047, 495.90896453111964, 536.5909361719027, 568.2468125670257, 
                   617.9945982444297, 672.2603963935339, 712.9920165230169, 749.1956944830599, 
                   789.9173849148033, 817.1148270246658, 835.2861738888669, 862.5034753942091, 
                   880.7344004448505, 889.8796520633912, 889.9491599475712, 876.5043492076102, 
                   872.0955634110496, 872.1948603884498, 854.2022480835685, 845.2456607220875, 
                   840.8269452277873, 822.8343329229056, 795.9248520475035, 764.5072883981411, 
                   728.5319934861182, 701.6026532152364, 674.6832426420942, 638.727807125551, 
                   607.3003137784485, 575.8728204313461, 539.937244310283, 513.0376931326209, 
                   486.088493466259, 441.1665408904955, 396.25451801247164, 360.33880128688907, 
                   306.3510346745047, 247.8253961949399, 202.81407633951585, 139.7505659927715, 
                   76.71684473924643, 40.71176073400329, 18.18127656194156],
                  [1.0922667514001034, 4.317432577352363, 6.883266473368565, 10.104460420224825, 
                   14.612543194185193, 19.12856972633756, 20.411486674345667, 22.361679310481804, 
                   25.61464829010606, 28.863645390634332, 33.44322198832268, 37.367438535171004, 
                   41.28768320292335, 47.19783929777179, 53.775271080748325, 61.00409103546892, 
                   71.53751439806177, 78.78222186916634, 83.39754537871872, 90.66211224530329, 
                   97.91873535369587, 104.5120546530564, 109.8025976089288, 115.08519680660922, 
                   121.68248798506576, 126.97303094093817, 140.18350081423526, 154.05727449656433, 
                   165.2976923382453, 177.18949835167015, 189.74063629503124, 202.29971799658423, 
                   215.51415974897728, 228.72860150137038, 242.60634706279544, 256.47614886602855, 
                   267.04929101958146, 284.2316399888788, 302.0733208881122, 317.2697303094094, 
                   332.4820272470906, 346.3796322039958, 357.62799380386866, 370.2109067799977, 
                   384.7718155459348, 394.03423759780753, 398.0100885729039],
                  'line']
    }

def read_paths(filename):
    with open(filename, "r") as file:
        paths = [line.replace("\n","") for line in  file.readlines()]
    for i in range(len(paths)):
        if paths[i][0] == '/':
            paths[i] = paths[i][1:]
        if paths[i][-1] == '/':
            paths[i] = paths[i][:-1]

    return paths

def run_systems(paths):
    '''
    Run system objects in parallel
    return: dictionary of systems
    '''
    global experimental_data
    system_objects = dict()
    system_objects['paths'] = paths
    for path in paths:
        objects = [coordinate_visualisation(),
                    pt_diagram(experimental_data),
                    temperature(),
                    pressure(),
                    energy_distribution_ion('potential'), energy_distribution_ion('kinetic'),
                    energy_distribution_electron('potential'), energy_distribution_electron('kinetic'),
                    energy_distribution_electron_full(),
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

def get_main_layout(common_pt, common_neighbour):
    return html.Div([
    # represents the URL bar, doesn't render anything
    html.H1("Hydrogen observation"),
    html.Div(common_pt.layout()),
    html.Div(common_neighbour.layout()),
    dcc.Location(id='url', refresh=False),
    # content will be rendered in this element
    html.Div(id='page-content')]
    )

def set_objects_app(app, system_objects):
    for path in system_objects['paths']:
        system_objects[path].set_app(app)

def add_items_in_dict(my_dict, items, my_object):
    if len(items) == 1:
        my_dict[items[0]] = my_object
        return
    if items[0] in my_dict:
        add_items_in_dict(my_dict[items[0]], items[1:], my_object)
        return
    my_dict[items[0]] = dict()
    add_items_in_dict( my_dict[items[0]], items[1:], my_object)

    return

def add_items_to_string(system_object, layout_list, items, tabs):
    if not type(items) is dict:
        #print ("items", items)
        layout_list.append(dcc.Markdown("**" + tabs + ">**[" + items.get_title() + "](/" + items.get_path() + ")"))
        #layout_list.append( html.Br())
        
        return #layout_list
    for item in items:
        if type(items[item]) is dict:
            layout_list.append(dcc.Markdown("**" + tabs + item + "**"))
            add_items_to_string(system_object, layout_list, items[item], tabs + "|---")
        else:
            add_items_to_string(system_object, layout_list, items[item], tabs)
    
    return 

def get_layout_list(system_objects):
    '''
    Get and update list of titles
    return: layout list of title html-structure
    '''
    layout_list =[]
    layout_dict = dict()
    for path in system_objects['paths']:
        our_path = path.split("/")
        #print (our_path)
        add_items_in_dict( layout_dict, our_path, system_objects[path])
        #if not path in system_objects:
        #    continue # this work is not finished, should wait
        #title = system_objects[path].get_title()

        #layout_list.append( dcc.Link(title, href="/" + path) )
        #layout_list.append( html.Br())
    #new_layout = []
    add_items_to_string(system_objects, layout_list, layout_dict, "")
    layout_list.append(html.Div("--------------------------------------------------------------",
        style={'color': 'black', 'fontSize': 18}))
    layout_list.append(html.Div("--------------------------------------------------------------",
        style={'color': 'black', 'fontSize': 18}))
    layout_list.append(html.Div("Data was obtained using Open Source LAMMPS packet.",
        style={'color': 'grey', 'fontSize': 12}))
    layout_list.append(html.Div("If you have any question, e-mail: ilya.d.fedorov@phystech.edu", 
        style={'color': 'grey', 'fontSize': 12}))

    return layout_list

if __name__ == "__main__":
    app = set_app()

    paths = read_paths("input.txt")
    system_objects = run_systems(paths)
    common_pt = common_pt_diagram(experimental_data)
    common_pt.analyse(system_objects)
    common_pt.add_app(app, page='url')
    common_neighbour = common_neighbour_distribtution(COMMON_PHRASE_FOR_NEIGHBOUR)
    common_neighbour.analyse(system_objects)
    common_neighbour.add_app(app, page='url')
    app.layout = get_main_layout(common_pt, common_neighbour)
    set_objects_app(app, system_objects)

    @app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
    def display_page(pathname):
        common_pt.analyse(system_objects)
        common_neighbour.analyse(system_objects)
        if not pathname:
            return html.Div(get_layout_list(system_objects))

        pathname_real = pathname[1:] # remove '/'
        if pathname_real in system_objects['paths']:
            return system_objects[pathname_real].get_layout()
        else:
            return html.Div(get_layout_list(system_objects))

    app.css.append_css({
        'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
    })

    app.run_server(port = PORT, host = '0.0.0.0')

