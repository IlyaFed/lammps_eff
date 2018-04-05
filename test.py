from lib.system import system
from lib.coordinate_visualisation import coordinate_visualisation
from lib.temperature import temperature
from lib.energy_distribution_ion import energy_distribution_ion
from lib.energy_distribution_electron import energy_distribution_electron
from lib.energy import energy
from lib.neighbour_distribution import neighbour_distribution
from lib.pt_diagram import *

experimental_data = {
    'Knudson': np.array([[900, 1250, 1600, 1700], [310, 290, 285, 285]]),
    'Loubeyre': np.array([[2000, 3000, 350, 350], [110, 50, 40, 25]]),
    'Ohta': np.array([[1750, 2200], [105, 85]]),
    'Silvera': np.array([[1100, 1300, 1400, 1600, 1750], [160, 150, 140, 120, 110]])
}

path = './test/'

objects = [coordinate_visualisation(),
           pt_diagram(experimental_data),
           temperature(),
           energy_distribution_ion('potential'), energy_distribution_ion('kinetic'),
           energy_distribution_electron('potential'), energy_distribution_electron('kinetic'),
           energy(),
           neighbour_distribution()]



hydrogen = system(path = path, objects = objects, server = 1, minstep = 5000)
