#!/usr/bin/bash

VOLUME=${1:-/tmp/volume1/}
MASTER=${2:-localhost:3000}
uwsgi --http :${PORT:-3000} --wsgi-file src/run.py --callable master --master --processes 4
