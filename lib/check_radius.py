# it's a common class of all system object
from lib.common_object import *
import numpy as np
from plotly import figure_factory as ff
from skimage import measure
import ctypes


class check_radius:
    def analyse(self, data, gen_info):
        self.data = data
        #print ("data: ", self.data)
        self.gen_info = gen_info
        # create coord_ion and coord_electron columns
        if "radius_check" in self.gen_info:
            return self.gen_info['radius_check']
        # read ions coordinates
        for Step in self.data.index:
            part_index = self.analyse_radius(Step)
            if part_index >= 0:
                self.gen_info['radius_check'] = "Radius check: crash at step {:d} for ID {:d}".format(
                    Step, part_index)
                return "Radius check: crash at step {:d} for ID {:d}".format(Step, part_index)
        self.gen_info['radius_check'] = "Radius check: ok"
        return "Radius check: ok"

    def analyse_radius(self, Step):
        parametrs = self.data.loc[Step, 'every']
        # read electron coordinates
        our_param = parametrs[parametrs['type'] == 2.0]
        n = our_param.shape[0]
        for i in range(n):
            if our_param.loc[our_param.index[i], 'c_1a[2]'] > self.max_radius:
                return i
        return -1

    def __init__(self, max_radius=5.0):
        self.max_radius = max_radius
