from lib.system import *
from lib.coordinate_visualisation import *
from lib.temperature import *
from lib.energy_distribution_ion import *
from lib.energy_distribution_electron import *
from lib.energy import *
from lib.pt_diagram import *

path = './test/all'
logfile = './test/log.lammps'
objects = [coordinate_visualisation(),
           pt_diagram(),
           temperature(),
           energy_distribution_ion('potential'), energy_distribution_ion('kinetic'),
           energy_distribution_electron('potential'), energy_distribution_electron('kinetic'),
           energy()]

hydrogen = system(lammpstrj = path, logfile = logfile, objects = objects, server = 1, minstep = 30000)
