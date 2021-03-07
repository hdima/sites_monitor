DOCKER_OPTIONS := -v $$(pwd):/build --network host
DOCKER := docker run --rm -ti ${DOCKER_OPTIONS} build-machine $$(id -u) $$(id -g)

.PHONY: all
all: check test build-sites_monitor

.PHONY: build-sites_monitor
build-sites_monitor: clean-sites_monitor
	@# -OO will discard docstrings
	${DOCKER} sh -c "python3 -OO -m compileall -j0 -f -b sites_monitor \
	                 && zip -r -9 docker/sites_monitor/sites_monitor.zip sites_monitor/*.pyc"
	docker build --pull -t sites_monitor docker/sites_monitor

.PHONY: test
test:
	${DOCKER} sh -c "coverage run --source sites_monitor,sites_reporter -m unittest discover -c \
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

.PHONY: clean-sites_monitor
clean-sites_monitor:
	rm -f docker/sites_monitor/sites_monitor.zip

.PHONY: clean
clean: clean-sites_monitor
	find . -name '*.py[co]' -delete
	find . -name __pycache__ -delete
	rm -rf .check_report .mypy_cache .coverage .test_report
