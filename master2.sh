#!/usr/bin/bash

DB=${1:-/tmp/cachedb/}
uwsgi --http :${PORT:-3001} --wsgi-file src/run.py --callable volume --master --processes 4
