#!/usr/bin/bash
uwsgi --http :${PORT:-3001} --wsgi-file src/run.py --callable volume --master --processes 4
