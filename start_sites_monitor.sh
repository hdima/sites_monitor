#! /bin/sh

exec docker run --rm -v $(pwd):/opt/sites_monitor sites_monitor "$@"
