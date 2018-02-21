import pandas as pd
import numpy as np
import os
from subprocess import Popen, PIPE

class load:
    def load_lammpstrj(self, path):
        """
        Read lammpstrj file and apply function
        :param path: path to you lammpstr files
        """
        print ( "\r{:30s} ".format("read lammpstrj"), end = '')
        if path[-1] != '/':
            path = path + '/'

        llist = np.array([])
        for msdfile in os.listdir(path):
            if msdfile.split('.')[-1] == 'lammpstrj':
                llist = np.append(llist, [int(msdfile.split('.')[1])])
        llist.sort()
        if int(llist[0]) == 0:
            self.start = int(llist[1])
        else:
            self.start = int(llist[0])
        self.step = max(int(llist[1] - llist[0]), self.minstep)
        self.stop = int(llist[-1])
        self.start = self.stop - 20* self.step # TODO !!!!!!
        self.wall = np.array([0, 0, 0], dtype=float)

        del llist

        for read_step in range(self.start, self.stop + self.step, self.step):
            print ("\r{:30s} {:3d} %".format("read lammpstrj", int(100.*(read_step-self.start)/(self.stop-self.start + self.step) )), end = '')
            file_name = "all.{:d}.lammpstrj".format(read_step)
            try:
                os.stat(path + file_name)
            except:
                continue
            for num_line, line in enumerate(open(path + file_name, "r")):

                if num_line == 5:
                    self.wall[0] = float( line.split(" ")[1] )
                if num_line == 6:
                    self.wall[1] = float( line.split(" ")[1] )
                if num_line == 7:
                    self.wall[2] = float( line.split(" ")[1] )

                if num_line == 8:
                    line = line.split(" ")[:-1]
                    columns_names = line[2:]
                    step_pandas = pd.DataFrame(columns=columns_names)
                if num_line > 8:
                    line = line.split(" ")[:-1]
                    step_pandas.loc[len(step_pandas)] = [float(word) for word in line]
            step_pandas.sort_values(by='id', inplace=True)
            for object in self.objects:
                object.load_step({'Step': read_step, 'parametrs': step_pandas, 'wall': self.wall})
        print ("\r{:30s} 100 %".format("read lammpstrj"))

    def load_step(self, path):
        """
        Read lammpstrj file and apply function
        :param path: path to you lammpstr files
        """
        if path[-1] != '/':
            path = path + '/'

        llist = np.array([])
        for msdfile in os.listdir(path):
            if msdfile.split('.')[-1] == 'lammpstrj':
                llist = np.append(llist, [int(msdfile.split('.')[1])])
        llist.sort()
        self.start = int(llist[0])
        self.step = max(int(llist[1] - llist[0]), self.minstep)
        self.stop = int(llist[-1])
        del llist

    def load_log(self, name):
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
        p = Popen(["wc", "-l", "{:s}".format(name)], stdout=PIPE)
        line_in_file = int(str(p.stdout.read()).split("b'")[1].split(name)[0])
        start_flag = 1
        read_flag = 0
        for num_line, line in enumerate( open( name, 'r')):
            if (line[0] == 'S') and  (line.split()[0] == 'Step') and (read_flag == 0):
                if start_flag:
                    data = pd.DataFrame(columns=line.split())
                    start_flag = 0
                read_flag = 1
                continue
            if read_flag:
                print ( "\r{:30s} {:3d} %".format("read lammps log", int(num_line/line_in_file * 100)), end = '')
                try:
                    data.loc[len(data)] = [float(i) for i in line.split()]
                except ValueError:
                    read_flag = 0
        print("\r{:30s} {:3d} %".format("read lammps log", 100))
        data['Step'] = data['Step'].astype(int)
        data = data[ (data['Step'] - self.start) % self.step == 0]
        for object in self.objects:
            object.load_log(data)
        del read_flag, data
        print ( "\ncomplete" )

    def __init__(self, objects, minstep):
        self.objects = objects
        self.minstep = minstep

