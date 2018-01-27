import sys
import lib.read as rd

def test_log():
    name = './test/log.lammps'
    log = rd.log()
    if (log.test(name=name) == 0):
        print ("----success test log----")
    else:
        print ("----fail test log----")

def test_lammpstrj():
    path = './test/all'
    lammpstrj = rd.lammpstrj()
    if (lammpstrj.test(path = path) == 0):
        print ("----success test lammpstrj----")
    else:
        print ("----fail test lammpstrj----")

def test_all():
    test_log()
    test_lammpstrj()
    print ("----success test all function----")

arguments = {
        'log': test_log,
        'lammpstrj': test_lammpstrj,
        'all': test_all
        }

arguments[sys.argv[1]]()


