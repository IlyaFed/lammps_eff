all: dash

install:
	g++ -shared -O3 -Wall -fPIC -o lib/grid_gauss.so lib/grid_gauss.c
	g++ -shared -O3 -Wall -fPIC -o lib/neigbour.so lib/neighbour.c

dash: install
	python3 start.py

test_log: test.py
	python3 test.py log

test_lammpstrj:
	python3 test.py lammpstrj

test:
	python3 test.py all
