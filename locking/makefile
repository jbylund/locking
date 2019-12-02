SHELL := /bin/bash
REDIS_PORT := 9123
DYNAMODB_PORT := 9124
.DEFAULT_GOAL := post_tests

.PHONY: \
	post_tests \
	pre_tests \
	start_dynamodb \
	start_redis \
	stop_dynamodb \
	stop_redis \
	tests \

pre_tests: start_redis start_dynamodb

start_redis:
	docker run --detach --publish $(REDIS_PORT):6379 redis:latest

stop_redis: tests
	/usr/bin/docker ps --filter ancestor=redis:latest  --format {{.ID}} | xargs -n 1 /usr/bin/docker kill

start_dynamodb:
	docker run --detach --publish $(DYNAMODB_PORT):8000 amazon/dynamodb-local:latest

stop_dynamodb: tests
	/usr/bin/docker ps --filter ancestor=amazon/dynamodb-local:latest  --format {{.ID}} | xargs -n 1 /usr/bin/docker kill

tests: pre_tests
	DYNAMODB_PORT=$(DYNAMODB_PORT) REDIS_PORT=$(REDIS_PORT) timeout 90s python -m pytest > /dev/null || \
		DYNAMODB_PORT=$(DYNAMODB_PORT) REDIS_PORT=$(REDIS_PORT) timeout 90s python -m pytest -vvv --last-failed

post_tests: tests stop_redis stop_dynamodb
