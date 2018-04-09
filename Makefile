all: main

install:
	g++ -shared -O3 -Wall -fPIC -o lib/grid_gauss.so lib/grid_gauss.c
	g++ -shared -O3 -Wall -fPIC -o lib/neighbour.so lib/neighbour.c

main:
	python3 main.py

silence:
	python3 main.py > log.log 2>>log.log &

clean_backup:
	rm -f ./test_data/.backup
