pre-commit:
	pre-commit run --all-files

test: unittest

unittest:
	pytest

tdd:
	ptw --poll -- -vv

coverage:
	pytest --cov-report html --cov-report xml
