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
import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np
from multiprocessing.dummy import Pool as ThreadPool


# from telegraph import Telegraph

# telegraph = Telegraph()

# telegraph.create_account(short_name='Ilya Fedorov')

# response = telegraph.create_page(
#     'Hey',
#     html_content='<p>Hello, world!</p>'
# )

# print('http://telegra.ph/{}'.format(response['path']))

experimental_data = {
    'Knudson': np.array([[900, 1250, 1600, 1700], [310, 290, 285, 285]]),
    'Loubeyre': np.array([[2000, 3000, 350, 350], [110, 50, 40, 25]]),
    'Ohta': np.array([[1750, 2200], [105, 85]]),
    'Silvera': np.array([[1100, 1300, 1400, 1600, 1750], [160, 150, 140, 120, 110]])
}

with open("input.txt", "r") as file:
    paths = [line.replace("\n","") for line in  file.readlines()]


port = 8050
system_objects = dict()

def start_proc(path):
    objects = [coordinate_visualisation(),
               pt_diagram(experimental_data),
               temperature(),
               pressure(),
               energy_distribution_ion('potential'), energy_distribution_ion('kinetic'),
               energy_distribution_electron('potential'), energy_distribution_electron('kinetic'),
               energy(),
               neighbour_distribution(),
               rdf()]
    global system_objects
    system_objects[path] = system(path = path, objects = objects)



# Make the Pool of workers
pool = ThreadPool(len(paths))

#ThreadPool Open the urls in their own threads
# and return the results
results = pool.map(start_proc, paths)

#close the pool and wait for the work to finish
pool.close()
pool.join()
 #TODO 
 
app = dash.Dash()
app.config.suppress_callback_exceptions = True
app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),
    # content will be rendered in this element
    html.Div(id='page-content')]
)

layout_list = []
layout_object = dict()
for path in paths:
    title = system_objects[path].get_title()
    layout_object[path] = system_objects[path].get_layout()
    system_objects[path].set_app(app)
    layout_list.append( dcc.Link(title, href="/" + path) )
    layout_list.append( html.Br())

index_page = html.Div(layout_list)


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if not pathname:
        return index_page
    pathname_real = pathname[1:] # without '/'
    if pathname_real in paths:
        return system_objects[pathname_real].get_layout()
    else:
        return index_page

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

app.run_server(port = port, host = '0.0.0.0')


