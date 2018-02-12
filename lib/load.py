import pandas as pd
import numpy as np
import os

class load:
    def load_lammpstrj(self, path):
        """
        Read lammpstrj file and apply function
        :param path: path to you lammpstr files
        """
        print ( "\rread lammpstrj:", end = '')
        if path[-1] != '/':
            path = path + '/'

        llist = np.array([])
        for msdfile in os.listdir(path):
            if msdfile.split('.')[-1] == 'lammpstrj':
                llist = np.append(llist, [int(msdfile.split('.')[1])])
        llist.sort()
        self.start = int(llist[0])
        self.step = int(llist[1] - llist[0])
        self.stop = int(llist[-1])
        del llist

        for read_step in range(self.start, self.stop + self.step, self.step):
            print ("\rread lammpstrj: ({:2d} %)".format(int(100.*(read_step-self.start)/(self.stop-self.start + self.step))), end = '')
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
            for object in self.objects:
                object.load_step(read_step, step_pandas)
        print ("\rread lammpstrj: (100 %)")


    def load_log(self, name):
        #TODO доделать эту часть, она не объектно ориентированна
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

    def __init__(self, objects):
        self.objects = objects

