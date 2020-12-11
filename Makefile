all:

clean:
	-rm *~ *.pyc
install:
	./setup.py build && sudo ./setup.py install
