Sites monitor
=============

*WARNING: Work in progress project!*

Distributed application to monitor status of configured sites and report it to
a PostgreSQL database through a Kafka topic.

Prerequisites
-------------

The main prerequisites are the following:

- Installed `docker`
- Installed `make` tool (GNU `make` is preferred)

Build and tests
---------------

Build process requires the build machine image to be built with the following command:

```
make build-machine
```

After that the following main `make` targets are available:

- `make all` (default target) - run all checks, tests and build `sites_monitor` Docker image
- `make test` - run unit tests
- `make check` - run static code checks
- `make clean` - remove build artefacts
- `make python` - run Python shell in context of the build machine
- `make build-shell` - run Bash shell in context of the build machine

Sites monitor
-------------

After building Docker image for `sites_monitor` with `make all` command it can
be started with the following command:

```
./start_sites_monitor.sh --config sites_monitor.conf
```

See `example_sites_monitor.conf` for example configuration.

Sites reporter
--------------

*Not implemented. See TODO.md for more details*

Directories
-----------

- `sites_monitor` - Python package for sites monitor
- `sites_reporter` - Python package for sites reporter
- `docker` - configuration for Docker images
