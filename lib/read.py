import pandas as pd
import numpy as np
import os

class lammpstrj:
    data = 0
    ion_mass = 0
    electron_mass = 0
    ion_e_dist_grid = 100
    el_e_dist_grid = 100
    list_of_functions = dict()
    k_boltz = 1.3806485279e-23
    e_harty = 4.35974417e-18
    aem = 1.66e-27
    ab_atu = 0.529e-10/1e-15

    def read(self, path, functions, start, stop, step, m_i = 1, m_e = 1):
        """
        Read lammpstrj file and apply function
        :param path: path to you lammpstr files
        """
        self.ion_mass = m_i
        self.electron_mass = m_e

        print ( "\rread lammpstrj:", end = '')
        if path[-1] != '/':
            path = path + '/'

        self.data = pd.DataFrame(columns = ["Step"] + functions)

        for read_step in range(start, stop, step):
            print ("\rread lammpstrj: ({:2d} %)".format(int(100.*(read_step-start)/(stop-start))), end = '')
            file_name = "all.{:d}.lammpstrj".format(read_step)
            try:
                os.stat(path + file_name)
            except:
                continue
            for num_line, line in enumerate(open(path + file_name, "r")):
                line = line.split(" ")[:-1]
                if num_line == 8:
                    columns_names = line[2:]
                    step_pandas = pd.DataFrame(columns=columns_names)
                if num_line > 8:
                    step_pandas.loc[len(step_pandas)] = [float(word) for word in line]
            index = self.data.shape[0]
            self.data.loc[index, 'Step'] = read_step
            for func in functions:
                f = self.list_of_functions[func]
                self.data.loc[index, func] = f(step_pandas)
        print ("\rread lammpstrj: (100 %)")

    def T_electron_slow(self, parametrs):
        our_param = parametrs[parametrs['type'] == 2.0]
        def f_T_electron(param):
            v2 = param['vx']**2 + param['vy']**2 + param['vz']**2
            rad_v2 = param['c_1a[3]']**2
            return v2 + 0.75 * rad_v2
        v2_mean = our_param.apply(f_T_electron, axis=1).mean()
        return 2. / 4. / self.k_boltz * (self.electron_mass * self.aem) / 2 * (self.ab_atu**2 * v2_mean)

    def T_ion_slow(self, parametrs):
        our_param = parametrs[parametrs['type'] == 1.0]
        def f_T_ion(param):
            v2 = param['vx']**2 + param['vy']**2 + param['vz']**2
            return v2
        v2_mean = our_param.apply(f_T_ion, axis=1).mean()
        return 2. / 3. / self.k_boltz * (self.ion_mass * self.aem) / 2 * (self.ab_atu**2 * v2_mean)

    def T_electron(self, parametrs):
        our_param = parametrs[parametrs['type'] == 2.0]
        return 2. / 4. / self.k_boltz *  (our_param['c_keatom'].mean() * self.e_harty)

    def T_ion(self, parametrs):
        our_param = parametrs[parametrs['type'] == 1.0]
        return 2. / 3. / self.k_boltz *  ( our_param['c_keatom'].mean() * self.e_harty)

    def E_distribution_ion(self, parametrs):
        def sum_func(x):
            return x['c_peatom'] + x['c_keatom']

        energy = parametrs[parametrs['type'] == 1.0].apply(sum_func, axis = 1)
        e_max = energy.max()
        e_min = energy.min()
        e = np.zeros((2, self.ion_e_dist_grid+1))
        for i in range(self.ion_e_dist_grid + 1):
            e[0][i] = e_min + (e_max - e_min) / self.ion_e_dist_grid * i

        def f_e_dist(x):
            e[1][ int(( x - e_min ) / (e_max - e_min) * self.ion_e_dist_grid) ] += 1
            pass
        energy.apply(f_e_dist)

        return e

    def E_distribution_electron(self, parametrs):
        def sum_func(x):
            return x['c_peatom'] + x['c_keatom']

        energy = parametrs[parametrs['type'] == 2.0].apply(sum_func, axis = 1)
        e_max = energy.max()
        e_min = energy.min()
        e = np.zeros((2, self.el_e_dist_grid+1))
        for i in range(self.el_e_dist_grid+1):
            e[0][i] = e_min + (e_max - e_min) / self.el_e_dist_grid * i

        def f_e_dist(x):
            e[1][ int(( x - e_min ) / (e_max - e_min) * self.el_e_dist_grid) ] += 1
            pass
        energy.apply(f_e_dist)

        return e

    def Maxwell_e(self, parametrs):
        energy = parametrs[parametrs['type'] == 2.0].apply(lambda x: x['c_peatom'] + x['c_keatom'], axis = 1)
        e_max = energy.max()
        e_min = energy.min()
        e = np.zeros((2, self.el_e_dist_grid+1))
        for i in range(100):
            e[0][i] = e_min + (e_max - e_min) / 100. * i
#        Maxwell_ion = [E**0.5*np.exp(-3*E/2/T_ion)
        return 0

    def test(self, path):
        functions = ["T_e", "T_i", "E_dist_e", "E_dist_i"]
        self.read(path = path, functions = functions, start = 2000000, step = 100000, stop = 2300000, m_i = 1.008, m_e = 0.005)
        print (self.data)
        return 0

    def __init__(self):
        self.list_of_functions = {
            "T_e": self.T_electron,
            "T_e_slow": self.T_electron_slow,
            "T_i": self.T_ion,
            "T_i_slow": self.T_ion_slow,
            "E_dist_i": self.E_distribution_ion,
            "E_dist_e": self.E_distribution_electron,
        }

class log:
    data = 0
    def read(self, name):
        """
        Read date from lammps log
        :param name: full name of you log
        :return: pandas of date
        """
        print ( "\rread lammps log ... ", end = '')

        try:
            os.stat(name)
        except:
            print ("\nError (file not found)")
            pass

        read_flag = 0
        for num_line, line in enumerate( open( name, 'r')):
            if (line[0] == 'S') and  (line.split()[0] == 'Step') and (read_flag == 0):
                self.data = pd.DataFrame(columns=line.split())
                read_flag = 1
                continue
            if read_flag:
                print ( "\rread lammps log ({:6d} row)".format(num_line), end = '')
                try:
                    self.data.loc[len(self.data)] = [float(i) for i in line.split()]
                except ValueError:
                    read_flag = 0

        self.data['Step'] = self.data['Step'].astype(int)
        del read_flag
        print ( "\ncomplete" )


    def test(self, name):
        self.read(name = name)
        if (self.data.shape[0] == 1001):
            return 0
        return 1

    def __init__(self):
        pass
