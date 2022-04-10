#!/bin/bash
uwsgi --http :3000 --wsgi-file server.py --master --processes 4
