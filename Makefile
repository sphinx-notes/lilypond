LANG=en_US.UTF-8

MAKE = make
PY   = python3
RM   = rm -rf

.PHONY: doc
doc:
	$(MAKE) -C doc/

.PHONY: dist
dist: setup.py
	$(RM) dist/
	$(PY) setup.py sdist bdist_wheel

.PHONY: upload
upload: dist/
	$(PY) -m twine upload --repository pypi $<*
