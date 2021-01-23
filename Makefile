.PHONY: safety
safety:
	pipenv check

.PHONY: isort
isort:
	isort .

.PHONY: isort-check
isort-check:
	isort . --check

.PHONY: flake8
flake8:
	flake8 .

.PHONY: black
black:
	black .

.PHONY: black-check
black-check:
	black --check .

.PHONY: bandit
bandit:
	bandit -r *.py api/*.py torznab/*.py

.PHONY: mypy
mypy:
	mypy

.PHONY: pytype
pytype:
	pytype .

.PHONY: checks
checks: isort-check flake8 black-check bandit mypy pytype safety

.PHONY: tests
tests: 
	py.test --cov api --cov-report=xml --cov-report=term

.PHONY: format
format: isort black
