all: main

install:
	g++ -shared -O3 -Wall -fPIC -o lib/grid_gauss.so lib/grid_gauss.c
	g++ -shared -O3 -Wall -fPIC -o lib/neighbour.so lib/neighbour.c
	g++ -shared -O3 -Wall -fPIC -o lib/rdf_c.so lib/rdf_c.c

main:# clean
	rm -f log.log
	python3 main.py

silence:
	rm -f log.log
	bash -c "exec -a lammps_eff python3 main.py 2> error.log &"

clean:
	rm -f ./test_data/.backup

test:
	rm -f log.log
	python3 test_system.py

test_http:
	rm -f log.log
	python3 test_http.py

show:
	ps -ef | grep lammps_eff

kill:
	pkill -f lammps_eff
