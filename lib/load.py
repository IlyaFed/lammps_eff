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


        # Here we choose lammpstrj file which we will reads
        if len(self.steps):
            for i in range(len(self.steps)):
                if not self.steps[i] in llist:
                    self.steps.del(i) # TODO need to delete this element
        else:
            llist.sort()
            start = int(llist[0])
            step = max(int(llist[1] - llist[0]), self.minstep)
            stop = int(llist[-1])
            self.steps = np.arange(start, stop+1, step)
            del start, stop, step

        self.wall = np.array([0, 0, 0, 0, 0, 0], dtype=float)

        del llist

        iteration_number = 0
        iteration_len = len(self.steps)

        for read_step in self.steps:
            print ("\r{:30s} {:3d} %".format("read lammpstrj", int(100.* iteration_number/iteration_len )), end = '')
            iteration_number += 1
            file_name = "all.{:d}.lammpstrj".format(read_step)
            n = 0
            for num_line, line in enumerate(open(path + file_name, "r")):
                if num_line == 3:
                    n = float( line )
                if num_line == 5:
                    self.wall[0] = float( line.split(" ")[1] )
                    self.wall[3] = float( line.split(" ")[0] )
                if num_line == 6:
                    self.wall[1] = float( line.split(" ")[1] )
                    self.wall[4] = float( line.split(" ")[0] )
                if num_line == 7:
                    self.wall[2] = float( line.split(" ")[1] )
                    self.wall[5] = float( line.split(" ")[0] )

                if num_line == 8:
                    line = line.split(" ")[:-1]
                    columns_names = line[2:]
                    step_pandas = pd.DataFrame(columns=columns_names)
                if ( (num_line > 8) & (num_line < 9 + n) ):
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
        try:
            line_in_file = int(str(p.stdout.read()).split("b'")[1].split(name)[0])
        except:
            print ("error get number of lines in file")
            line_in_file = 100
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

    def __init__(self, objects, minstep, custom_steps):
        self.objects = objects
        self.minstep = minstep
        if len(custom_steps):
            self.steps = custom_steps
        else:
            self.steps = []



