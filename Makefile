all: test

test:
	poetry run pytest --cov sugarjazy --cov-fail-under 75
	poetry run pylint ./sugarjazy ./tests
