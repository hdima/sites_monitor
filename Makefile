DOCKER_OPTIONS := -v $$(pwd):/build --network host
DOCKER := docker run --rm -ti ${DOCKER_OPTIONS} build-machine $$(id -u) $$(id -g)

.PHONY: all
all: check test

.PHONY: test
test:
	${DOCKER} sh -c "coverage run -m unittest discover -c \
	                 && coverage report && coverage html -d .test_report"

.PHONY: check
check:
	${DOCKER} mypy --html-report .check_report --txt-report .check_report -p sites_monitor -p sites_reporter
	cat .check_report/index.txt

.PHONY: python
python:
	${DOCKER} python3

.PHONY: build-shell
build-shell:
	${DOCKER} bash

.PHONY: build-machine
build-machine:
	docker build --pull -t build-machine docker/build-machine

.PHONY: clean
clean:
	rm -rf .check_report .mypy_cache .coverage .test_report
