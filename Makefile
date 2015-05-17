export PYTHONPATH:=.:$(PYTHONPATH)

run:
	python appserver.py --port=9001
