LANG=en_US.UTF-8

MAKE = make
PY   = python3

.PHONY: doc
doc:
	$(MAKE) -C doc/

.PHONY: dist
dist: setup.py
	$(PY) setup.py sdist
