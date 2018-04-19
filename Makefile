all: main

install:
	g++ -shared -O3 -Wall -fPIC -o lib/grid_gauss.so lib/grid_gauss.c
	g++ -shared -O3 -Wall -fPIC -o lib/neighbour.so lib/neighbour.c
	g++ -shared -O3 -Wall -fPIC -o lib/rdf_c.so lib/rdf_c.c

main: clean
	python3 main.py

silence:
	rm -f log.log
	python3 main.py &

clean:
	rm -f ./test_data/.backup
