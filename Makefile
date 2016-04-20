PROJECT_DIR=$(shell pwd)
VENV_DIR?=$(PROJECT_DIR)/.env
PIP?=$(VENV_DIR)/bin/pip
PYTHON?=$(VENV_DIR)/bin/python
NOSE?=$(VENV_DIR)/bin/nosetests

.PHONY: all clean test run pip virtualenv

all: clean virtualenv pip

virtualenv:
	virtualenv $(VENV_DIR)

pip: requirements

requirements:
	$(PIP) install -r $(PROJECT_DIR)/requirements.txt

test:
	$(NOSE) $(PROJECT_DIR) --verbose

start:
	./manage.sh start

stop:
	./manage.sh stop

restart:
	./manage.sh restart

clean_temp:
	find . -name '*.pyc' -delete
	rm -rf .coverage dist docs/_build htmlcov MANIFEST

clean_redis:
	redis-cli flushall

clean_venv:
	rm -rf $(VENV_DIR)

clean: clean_temp clean_redis clean_venv

