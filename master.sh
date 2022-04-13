#!/bin/bash

export DB=${1:-/tmp/cachedb/}
export TYPE=master
uwsgi --http :${PORT:-3000} --wsgi-file src/run.py --callable master --master --processes 4