all: test

install:
	g++ -shared -O3 -Wall -fPIC -o lib/grid_gauss.so lib/grid_gauss.c
	g++ -shared -O3 -Wall -fPIC -o lib/neighbour.so lib/neighbour.c

test: test.py
	python3 test.py

clean_backup:
	rm -f ./test_data/.backup
