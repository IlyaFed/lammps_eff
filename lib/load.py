import pandas as pd
import numpy as np
import os
import glob # to recursive find files
from subprocess import Popen, PIPE
import pickle
import logging

min_timeperiod = 100 # 100 fs

class load:

    def load_lammpstrj(self):
        """
        Read lammpstrj file and apply function
        """
        logging.info ("{:30s} ({:s}) {:3d} %".format("read lammpstrj", self.path, 0))
        try:
            lammpstrj_path_tmp = glob.glob(self.path + '/**/**/all.0.lammpstrj', recursive=True)[0].split('/')[:-1]
        except IndexError:
            print ("error: must be all.0.lammpstrj file")
            exit()

        lammpstrj_path = ''
        for item in lammpstrj_path_tmp:
            lammpstrj_path += item + '/'


        available_lammpstrj = np.array([])
        for msdfile in os.listdir(lammpstrj_path):
            if msdfile.split('.')[-1] == 'lammpstrj':
                available_lammpstrj = np.append(available_lammpstrj, [int(msdfile.split('.')[1])])

        if self.load_log_flag: 
            # if self.data exist, clear step which we can't load from lammpstrj
            to_remove = []
            for i in self.data.index:
                if not i in available_lammpstrj:
                    to_remove.append(i)
            self.data.drop(to_remove, inplace=True)
        else:
            # reduce number of steps
            min_step = int(min_timeperiod / 0.005 /1000) * 1000 # step equal 100 fs and must diveded into 1000, approximate step as 0.005 fs
            self.steps = []
            indexes = available_lammpstrj
            buf_step = indexes[0]
            max_step = max(indexes)
            while (buf_step <= max_step):
                previous_step = buf_step - min_step
                next_step = buf_step + min_step
                buf_step_next = buf_step,
                buf_step_prev = buf_step-1
                while (buf_step_next < next_step) and (buf_step_prev > previous_step):
                    if buf_step_next in indexes:
                        self.steps.append(buf_step_next)
                        break
                    if buf_step_prev in indexes:
                        self.steps.append(buf_step_prev)
                        break
                buf_step = next_step
            if len(self.steps) < 2:
                logging.error ("Number of steps in load lammpstrj too small: {:d}, step of analysis: {:d}".format(len(self.steps), min_step))
                exit()
        
            self.data = pd.DataFrame(columns=['every', 'wall'], index = self.steps)
        
        # create pandas
        
        iteration_number = 0
        print_list = [30, 60]
        iteration_len = len(self.steps)
        for read_step in self.steps:
            if len(print_list) and ( 100.* iteration_number/iteration_len > print_list[0] ):
                logging.info("{:30s} ({:s}) {:3d} %".format("read lammpstrj", self.path, print_list[0]))
                del ( print_list[0] )
            iteration_number += 1
            file_name = "all.{:d}.lammpstrj".format(read_step)
            n = 0
            wall = np.zeros(6)
            for num_line, line in enumerate(open(lammpstrj_path + file_name, "r")):
                if num_line == 3:
                    n = int( line )
                    self.general_info['n'] = n
                if num_line == 5:
                    wall[0] = float( line.split(" ")[0] )
                    wall[3] = float( line.split(" ")[1] )
                if num_line == 6:
                    wall[1] = float( line.split(" ")[0] )
                    wall[4] = float( line.split(" ")[1] )
                if num_line == 7:
                    wall[2] = float( line.split(" ")[0] )
                    wall[5] = float( line.split(" ")[1] )

                if num_line == 8:
                    line = line.split(" ")[:-1]
                    columns_names = line[2:]
                    step_pandas = pd.DataFrame(columns=columns_names)
                if ( (num_line > 8) & (num_line < 9 + n) ):
                    line = line.split(" ")[:-1]
                    step_pandas.loc[len(step_pandas)] = [float(word) for word in line]
            #print ("read_step:", read_step)

            step_pandas.sort_values(by='id', inplace=True)
            #print ("step_pandas: ", step_pandas)
            step_pandas.loc[:, 'x'] -= wall[0]
            step_pandas.loc[:, 'y'] -= wall[1]
            step_pandas.loc[:, 'z'] -= wall[2] 
            wall[3] -= wall[0]
            wall[4] -= wall[1]
            wall[5] -= wall[2]
            wall = wall[3:]
            self.data.at[read_step, 'every'] = step_pandas
            self.data.at[read_step, 'wall'] = wall
            
        logging.info ("{:30s} ({:s}) 100 %".format("read lammpstrj", self.path))
        self.load_lammpstrj_flag = True

    def load_log(self):
        """
        Read date from lammps log
        :param name: full name of you log
        :return: pandas of date
        """
        logging.info ("{:30s} ({:s}) {:3d} %".format("read log", self.path, 0))
        try:
            name =  glob.glob(self.path + '/**/**/log.lammps', recursive=True)[0]
        except IndexError:
            logging.error ("error: must be log.lammps file")
            exit()

        if not self.load_lammpstrj_flag:
            self.data = pd.DataFrame(columns=['every', 'wall']) # TODO check available step in lammps and log
        
        p = Popen(["wc", "-l", "{:s}".format(name)], stdout=PIPE)
        try:
            line_in_file = int(str(p.stdout.read()).split("b'")[1].split(name)[0])
        except:
            logging.debug ("error: get number of lines in file fall")
            line_in_file = 100
        read_flag = 0
        print_list = [30,60]
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

                if len(print_list) and ( num_line/line_in_file * 100 > print_list[0] ):
                    logging.info ("{:30s} ({:s}) {:3d} %".format("read log", self.path, print_list[0]))
                    del ( print_list[0] )
                try:
                    line_data = [float(i) for i in line.split()[1:]]
                    Step = int( line.split()[0])
                    if Step % 1000:
                        continue
                    if (self.load_lammpstrj_flag) and (Step in self.data.index):
                        if len(columns) == len(line_data): # check that all data exists
                            for item in range( len(columns) ):
                                self.data.at[Step, columns[item]] = line_data[item]
                    if not self.load_lammpstrj_flag:
                        if len(columns) == len(line_data):
                            for item in range( len(columns) ):
                                self.data.at[Step, columns[item]] = line_data[item]

                except ValueError:
                    read_flag = 0
        if not self.load_lammpstrj_flag:
            # reduce number of steps
            min_step = int(min_timeperiod / self.general_info['timestep'] /1000) * 1000 # step equal 100 fs and must diveded into 1000
            self.steps = []
            indexes = self.data.index
            buf_step = indexes[0]
            max_steps = max(indexes)
            while (buf_step <= max_steps):
                previous_step = buf_step - min_step
                next_step = buf_step + min_step
                buf_step_next = buf_step
                buf_step_prev = buf_step-1000
                while (buf_step_next < next_step) and (buf_step_prev > previous_step):
                    if buf_step_next in indexes:
                        self.steps.append(buf_step_next)
                        break
                    if buf_step_prev in indexes:
                        self.steps.append(buf_step_prev)
                        break
                    buf_step_next += 1000
                    buf_step_prev -= 1000
                buf_step = next_step

            if len(self.steps) < 2:
                logging.error ("Number of steps in load log too small: {:d}, step of analysis: {:d}".format(len(self.steps), min_step))
                exit()
            # remove useless

            to_remove = []
            for i in self.data.index:
                if not i in self.steps:
                    to_remove.append(i)

            self.data.drop(to_remove, inplace=True)



        self.data['Press'] = self.data['Press'] / 1e9 # create GPa

        logging.info("{:30s} ({:s}) {:3d} %".format("read log",self.path,  100))
        del read_flag, columns

        self.load_log_flag = True

    def load_data(self):
        """
        Read date from lammps log
        :param name: full name of you log
        :return: pandas of date
        """
        #print ( "read data ({:s}) 0 %".format(self.path))
        try:
            name =  glob.glob(self.path + '/**/**/data.lammps', recursive=True)[0]
        except IndexError:
            logging.error ("error: must be data.lammps file, no timestep")
            exit()
            

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
            
        logging.info("read data ({:s}) success".format(self.path))

        self.load_data_flag = True

    def load_discription(self):
        try:
            filename =  glob.glob(self.path + '/**/**/description.txt', recursive=True)[0]
        except IndexError:
            logging.warning ("warning: no description.txt file")
            self.general_info['title'] = self.path
            self.general_info['description'] = 'no description file'
            return

        with open(filename, 'r') as myfile:
            data_from_file = myfile.readlines()
        self.general_info['title'] = data_from_file[0]
        self.general_info['description'] = ''
        for line in data_from_file[1:]:
            self.general_info['description'] += line + "\n"

    def load(self):
        ''' 
        Here we read directory to find files:
        log.lammps
        data.lammps
        all.0.lammpstrj -> directory with lammpstrj files
        
        Then start reading this files
        '''
        self.load_discription()
        self.load_data()
        self.load_log()    
        self.load_lammpstrj()
        
        self.load_objects()

    def load_objects(self):
        logging.info ("{:30s} ({:s}) {:3d} %".format("read objects", self.path, 0))
        new_flag = 0
        load_object_status = 0
        max_len = len(self.objects)
        print_list = [20, 40, 60, 80]
        for object in self.objects:
            load_object_status += 1
            if len(print_list) and ( load_object_status/max_len * 100 > print_list[0] ):
                    logging.info ("{:30s} ({:s}) {:3d} %".format("read objects", self.path, print_list[0]))
                    del ( print_list[0] )
            new_flag += object.analyse(self.data, self.general_info)
        logging.info ("{:30s} ({:s}) {:3d} %".format("read objects", self.path, 100))
        return new_flag
        
    def upload_backup(self, filename):
        backup_data = {'data': self.data, 'general_info': self.general_info}
        with open(filename, 'wb') as f:
            pickle.dump(backup_data, f)
        logging.info ("backup success")

    def load_backup(self, filename):
        logging.info ("load backup")
        with open(filename, 'rb') as f:
            backup_data = pickle.load(f)
        self.data = backup_data['data']
        self.general_info = backup_data['general_info']
        if self.load_objects():
            logging.info ("create updated backup")
            self.upload_backup(filename)
        logging.info ("backup has loaded")

    def __init__(self, objects, minstep, custom_steps, path):
        self.objects = objects
        self.minstep = minstep
        self.path = path
        self.general_info = {'mass': [0,0], 'timestep': 1.0}
        self.load_log_flag = False
        self.load_lammpstrj_flag = False

        if len(custom_steps):
            self.steps = custom_steps
        else:
            self.steps = []