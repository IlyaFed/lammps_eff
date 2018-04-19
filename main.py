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
    path = [line.replace("\n","") for line in  file.readlines()]

print ("path: ", path)
print ("len_path: ", len(path))
port_item = 8051
port = dict()
for item in path:
    port[item] = port_item
    port_item += 1

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
    global port
    system(path = path, objects = objects, port = port[path])



# Make the Pool of workers
pool = ThreadPool(len(path))

#ThreadPool Open the urls in their own threads
# and return the results
results = pool.map(start_proc, path)

#close the pool and wait for the work to finish
pool.close()
pool.join()
 #TODO logging
