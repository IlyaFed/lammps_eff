from lib.system import *
from lib.coordinate_visualisation import *
from lib.temperature import *
from lib.energy_distribution import *
from lib.energy import *

path = './test/all'
objects = [coordinate_visualisation(), temperature(), energy_distribution_ion('potential'), energy_distribution_ion('kinetic'), energy()]
hydrogen = system(fileplace = path, objects = objects, filetype='lammpstrj')