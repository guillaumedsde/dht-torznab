.PHONY: safety
safety:
	pipenv check

.PHONY: isort
isort:
	isort .

.PHONY: flake8
flake8:
	flake8 .

.PHONY: black
black:
	black .

.PHONY: bandit
bandit:
	bandit -r .

.PHONY: mypy
mypy:
	mypy

.PHONY: pytype
pytype:
	pytype .

.PHONY: checks
checks: isort flake8 black bandit mypy pytype safety

