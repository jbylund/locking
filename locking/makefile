
.PHONY: tests

tests: 
	timeout 90s -- python -m pytest > /dev/null || timeout 90s -- python -m pytest -vvv --last-failed
