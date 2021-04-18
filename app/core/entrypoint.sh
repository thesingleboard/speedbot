#!/bin/bash
export 
gunicorn -b 0.0.0.0:8000 --reload --access-logfile prom-gunicorn_access.log --error-logfile prom-gunicorn_error.log --log-level debug --timeout 120 speed_api &
python speedbot.py &