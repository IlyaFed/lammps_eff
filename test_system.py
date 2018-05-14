from lib.system import system
from lib.coordinate_visualisation import coordinate_visualisation
from lib.temperature import temperature
from lib.temperature_h2 import temperature_h2
from lib.energy_h2 import energy_h2
from lib.distance_h2 import distance_h2
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
from threading import Thread

import numpy as np
#from multiprocessing.dummy import Pool as ThreadPool


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

def read_paths(filename):
    with open(filename, "r") as file:
        paths = [line.replace("\n","") for line in  file.readlines()]
    return paths

path = read_paths("input.txt")[0]
port = 8051




# Make the Pool of workers
#pool = ThreadPool(len(paths))

#ThreadPool Open the urls in their own threads
# and return the results
#results = pool.map(start_proc, paths)

#close the pool and wait for the work to finish
#pool.close()
#pool.join()
 #TODO 

# start analysing results


objects = [coordinate_visualisation(highlight_particles=[233, 234,235,236]),
            pt_diagram(experimental_data),
            temperature_h2(indexes_of_particle=[233, 234,235,236]),
            energy_h2(type='potential', indexes_of_particle=[233, 234,235,236]),
            energy_h2(type='full', indexes_of_particle=[233, 234,235,236]),
            distance_h2(indexes_of_particle=[233, 234,235,236]),
            temperature(),
            pressure(),
            energy(),
            neighbour_distribution(),
            rdf()]

system_objects = system(path = path, objects = objects)
system_objects.run_on_port(port = port)
