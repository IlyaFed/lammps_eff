import lib.system as system

path = './test/all'
functions = ['T_e', 'T_i', 'X']
df = system.system(start = 2000000, step = 100000, stop = 2300000, m_ion = 1.008, m_electron = 0.005, functions = functions)

df.read(path, 'lammpstrj')
df.show(['T_e', 'T_i', 'X'])
