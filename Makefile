export PYTHONPATH:=.:$(PYTHONPATH)

install:
	pip install -r requirements.txt

run:
	python appserver.py --port=9001

clean:
	redis-cli flushall

cleanall:
	rm -r *.pyc
