all: dash

dash:
	python3 start.py

test_log: test.py
	python3 test.py log

test_lammpstrj:
	python3 test.py lammpstrj

test:
	python3 test.py all
