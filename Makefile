all: main

install:
	g++ -shared -O3 -Wall -fPIC -o lib/grid_gauss.so lib/grid_gauss.c
	g++ -shared -O3 -Wall -fPIC -o lib/neighbour.so lib/neighbour.c
	g++ -shared -O3 -Wall -fPIC -o lib/rdf_c.so lib/rdf_c.c

main: clean
	python3 main.py

silence:
	python3 main.py > log.log 2>>log.log &

clean:
	rm -f ./test_data/.backup
