#!/usr/bin/bash

uwsgi --http :${PORT:-3000} --wsgi-file src/run.py --callable master --master --processes 4
