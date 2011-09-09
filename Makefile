.PHONY: clean-pyc ext-test test upload-docs docs audit

all: clean-pyc test

test:
	python setup.py test

audit:
	python setup.py audit

release:
	python scripts/make-release.py

tox-test:
	PYTHONDONTWRITEBYTECODE= tox

clean:
	find . -name '*.class' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +


docs:
	$(MAKE) -C docs html