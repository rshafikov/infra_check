module = icarus

test:
	pytest .

build:
	PBR_VERSION=0.1 python3 setup.py sdist

