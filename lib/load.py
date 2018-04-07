import pandas as pd
import numpy as np
import os
import glob # to recursive find files
from subprocess import Popen, PIPE
import pickle

class load:
    def load_lammpstrj(self, path):
        """
        Read lammpstrj file and apply function
        :param path: path to you lammpstr files
        """
        print ( "\r{:30s} ".format("read lammpstrj"), end = '')
        try:
            lammpstrj_path_tmp = glob.glob(path + '/**/**/all.0.lammpstrj', recursive=True)[0].split('/')[:-1]
        except IndexError:
            print ("error: must be all.0.lammpstrj file")
            return

        lammpstrj_path = ''
        for item in lammpstrj_path_tmp:
            lammpstrj_path += item + '/'

        path = lammpstrj_path

        if self.load_log_flag:
            self.start = self.data.index[0]
            self.step = self.data.index[1] - self.data.index[0]
            self.stop = self.data.index[-1]
            self.steps = self.data.index
        else:
            llist = np.array([])
            for msdfile in os.listdir(path):
                if msdfile.split('.')[-1] == 'lammpstrj':
                    llist = np.append(llist, [int(msdfile.split('.')[1])])


            # Here we choose lammpstrj file which we will reads
            if len(self.steps):
                for step in self.steps:
                    if not step in llist:
                        self.steps.remove(step) 
                        self.start = self.steps[0]
                        self.stop = self.steps[-1]
                        self.step = self.steps[1] - self.steps[0]
            else:
                llist.sort()
                self.start = int(llist[0])
                self.step = max(int(llist[1] - llist[0]), self.minstep)
                self.stop = int(llist[-1])
                self.steps = np.arange(self.start, self.stop+1, self.step)
                for step in self.steps:
                    if not step in llist:
                        self.steps.remove(step) 
                        self.start = self.steps[0]
                        self.stop = self.steps[-1]
                        self.step = self.steps[1] - self.steps[0]
            del llist
            self.data = pd.DataFrame(columns=['every', 'wall'], index = self.steps)
        self.wall = np.array([0, 0, 0, 0, 0, 0], dtype=float)

        

        # create pandas
        
        iteration_number = 0
        iteration_len = len(self.steps)

        for read_step in self.steps:
            print ("\r{:30s} {:3d} %".format("read lammpstrj", int(100.* iteration_number/iteration_len )), end = '')
            iteration_number += 1
            file_name = "all.{:d}.lammpstrj".format(read_step)
            n = 0
            for num_line, line in enumerate(open(path + file_name, "r")):
                if num_line == 3:
                    n = int( line )
                    self.general_info['n'] = n
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
            if not (read_step in self.data.index):
                self.data.at[read_step, 'wall'] = self.wall
                self.data.at[read_step,'every'] = step_pandas
            else:
                self.data.at[read_step, 'every'] = step_pandas
                self.data.at[read_step, 'wall'] = self.wall
            
        print ("\r{:30s} 100 %".format("read lammpstrj"))
        self.load_lammpstrj_flag = True


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

    def load_log(self, path):
        """
        Read date from lammps log
        :param name: full name of you log
        :return: pandas of date
        """
        print ( "\rread lammps log ... ", end = '')
        try:
            name =  glob.glob(path + '/**/**/log.lammps', recursive=True)[0]
        except IndexError:
            print ("error: must be log.lammps file")
            return

        if not self.load_lammpstrj_flag:
            self.data = pd.DataFrame(columns=['every', 'wall']) # TODO check available step in lammps and log
        
        p = Popen(["wc", "-l", "{:s}".format(name)], stdout=PIPE)
        try:
            line_in_file = int(str(p.stdout.read()).split("b'")[1].split(name)[0])
        except:
            print ("error: get number of lines in file fall")
            line_in_file = 100
        read_flag = 0
        for num_line, line in enumerate( open( name, 'r')):
            if (line[0] == 't') and  (line.split()[0] == 'timestep') and (read_flag == 0):
                self.general_info['timestep'] = float(line.split()[1])
            if (line[0] == 'S') and  (line.split()[0] == 'Step') and (read_flag == 0):
                columns = line.split()[1:]

                # create column for all parametrs
                for item in columns:
                    self.data = self.data.assign(item=np.zeros(self.data.shape[0]))
                read_flag = 1
                continue
            if read_flag:
                print ( "\r{:30s} {:3d} %".format("read lammps log", int(num_line/line_in_file * 100)), end = '')
                try:
                    line_data = [float(i) for i in line.split()[1:]]
                    Step = int( line.split()[0])
                    if (self.load_lammpstrj_flag) and (Step in self.data.index):
                        for item in range( len(columns) ):
                            self.data.at[Step, columns[item]] = line_data[item]
                    if not self.load_lammpstrj_flag:
                        for item in range( len(columns) ):
                            self.data.at[Step, columns[item]] = line_data[item]

                except ValueError:
                    read_flag = 0
        
        self.data['Press'] = self.data['Press'] / 1e9 # create GPa

        print("\r{:30s} {:3d} %".format("read lammps log", 100))
        del read_flag, columns

        self.load_log_flag = True

    def load_data(self, path):
        """
        Read date from lammps log
        :param name: full name of you log
        :return: pandas of date
        """
        print ( "\rread data ...", end = '')
        try:
            name =  glob.glob(path + '/**/**/data.lammps', recursive=True)[0]
        except IndexError:
            print ("warning: must be data.lammps file, no timestep")
            return
            

        mass_flag = 0
        for num_line, line in enumerate( open( name, 'r')):
            if num_line == 0:
                self.general_info['data_description'] = line
                continue
            if (line[0] == 'M') and  (line.split()[0] == 'Masses'):
                mass_flag = 1
                continue
            if not mass_flag == 0:
                mass_flag += 1
            if mass_flag == 3:
                self.general_info['mass'][0] = float(line.split()[1])
                continue
            if mass_flag == 4:
                self.general_info['mass'][1] = float(line.split()[1])
                break
            
        print("\rread data success")

        self.load_data_flag = True

    def load_discription(self, path):
        try:
            filename =  glob.glob(path + '/**/**/description.txt', recursive=True)[0]
        except IndexError:
            print ("warning: no description.txt file")
            self.general_info['title'] = path
            self.general_info['description'] = 'no description file'
            return

        with open(filename, 'r') as myfile:
            data_from_file = myfile.readlines()
        self.general_info['title'] = data_from_file[0]
        self.general_info['description'] = ''
        for line in data_from_file[1:]:
            self.general_info['description'] += line + "\n"

    def load(self, path):
        ''' 
        Here we read directory to find files:
        log.lammps
        data.lammps
        all.0.lammpstrj -> directory with lammpstrj files
        
        Then start reading this files
        '''
        
        self.load_discription(path)
        self.load_data(path)
        self.load_log(path)    
        self.load_lammpstrj(path)
        
        self.load_objects()

    def load_objects(self):
        new_flag = 0
        for object in self.objects:
            new_flag += object.analyse(self.data, self.general_info)
        
        return new_flag
        
    def upload_backup(self, filename):
        backup_data = {'data': self.data, 'general_info': self.general_info}
        with open(filename, 'wb') as f:
            pickle.dump(backup_data, f)
        print ("backup success")

    def load_backup(self, filename):
        print ("load backup")
        with open(filename, 'rb') as f:
            backup_data = pickle.load(f)
        self.data = backup_data['data']
        self.general_info = backup_data['general_info']
        self.start = self.data.index[0]
        self.step = self.data.index[1] - self.data.index[0]
        self.stop = self.data.index[-1]
        if self.load_objects():
            print ("create updated backup")
            self.upload_backup(filename)
        print ("backup has loaded")


    def __init__(self, objects, minstep, custom_steps):
        self.objects = objects
        self.minstep = minstep

        self.general_info = {'mass': [0,0], 'timestep': 1.0}
        self.load_log_flag = False
        self.load_lammpstrj_flag = False

        if len(custom_steps):
            self.steps = custom_steps
        else:
            self.steps = []



