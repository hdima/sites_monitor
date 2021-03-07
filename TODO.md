TODO
====

See also TODO and FIXME comments in the Python code for some future tasks / questions

Sites monitor
-------------

- Unit tests for `sites_monitor.main` module

Sites reporter
--------------

- PostgreSQL database schema
- Kafka consumer to consume messages from a configurable topic
- PostgreSQL reporter to save consumed site status messages
- Verify Kafka message according to a schema and optionally save invalid
  messages to a separate database table

General
-------

- System tests which should start Docker based Kafka and PostgreSQL and run
  system test scenarios
