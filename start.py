from lib.system import *
from lib.coordinate_visualisation import *
from lib.temperature import *
from lib.energy_distribution_ion import *
from lib.energy_distribution_electron import *
from lib.energy import *
from lib.pt_diagram import *

experimental_data = {
    'Knudson': np.array([[900, 1250, 1600, 1700], [310, 290, 285, 285]]),
    'Loubeyre': np.array([[2000, 3000, 350, 350], [110, 50, 40, 25]]),
    'Ohta': np.array([[1750, 2200], [105, 85]]),
    'Silvera': np.array([[1100, 1300, 1400, 1600, 1750], [160, 150, 140, 120, 110]])
}

path = './test/all'
logfile = './test/log.log'
objects = [coordinate_visualisation(),
           pt_diagram(experimental_data),
           temperature(),
           energy_distribution_ion('potential'), energy_distribution_ion('kinetic'),
           energy_distribution_electron('potential'), energy_distribution_electron('kinetic'),
           energy()]



hydrogen = system(lammpstrj = path, logfile = logfile, objects = objects, server = 1, minstep = 40000, backup_path=".backup/")
